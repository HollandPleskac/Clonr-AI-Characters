import json
import re

from loguru import logger
from opentelemetry import metrics, trace
from pydantic import BaseModel, ValidationError
from tenacity import retry, retry_if_exception_type, stop_after_attempt, wait_random

from app.settings import settings
from clonr import templates
from clonr.data_structures import (
    Document,
    Memory,
    MemoryWithoutRating,
    Message,
    Monologue,
    Node,
)
from clonr.llms import LLM, GenerationParams, LLMResponse, MockLLM
from clonr.templates.memory import MemoryExample
from clonr.templates.qa import Excerpt
from clonr.text_splitters import TokenSplitter
from clonr.tokenizer import Tokenizer

MAX_RETRIES = 3
RETRY_MIN = 0.1
RETRY_MAX = 1
MIN_CHUNK_SIZE = 256


tracer = trace.get_tracer(__name__)
meter = metrics.get_meter(settings.APP_NAME)

output_parsing_exception_meter = meter.create_counter(
    name="llm_output_parsing_exceptions",
    description="The number of times we could not properly parse the output of an LLM call",
)


class OutputParserError(Exception):
    pass


class QueryList(BaseModel):
    arr: list[str]


class ReflectionItem(BaseModel):
    insight: str
    memories: list[int]


class Params:
    agent_summary = GenerationParams(
        max_tokens=512, top_p=0.95, presence_penalty=0.3, temperature=0.6
    )
    long_description = GenerationParams(max_tokens=512, top_p=0.95, temperature=0.5)
    entity_context_create = GenerationParams(
        max_tokens=512, top_p=0.95, temperature=0.5
    )
    rate_memory = None  # (Jonny) these are LLM specific and determined dynamically to make sure we get ints out!
    message_queries_create = GenerationParams(
        max_tokens=256, top_p=0.95, presence_penalty=0.2, temperature=0.3
    )
    question_and_answer = GenerationParams(max_tokens=512, top_p=0.95, temperature=0.0)
    reflection_queries_create = GenerationParams(
        max_tokens=256, top_p=0.95, presence_penalty=0.2, temperature=0.3
    )
    reflection_create = GenerationParams(max_tokens=256, temperature=0.3, top_p=0.95)
    summarize = GenerationParams(
        max_tokens=512, temperature=0.3, presence_penalty=0.2, top_p=0.95
    )
    online_summarize = GenerationParams(
        max_tokens=512, temperature=0.3, presence_penalty=0.2, top_p=0.95
    )
    generate_zero_memory_message = GenerationParams(
        max_tokens=512, temperature=0.7, top_p=0.95
    )
    generate_long_term_memory_message = GenerationParams(
        max_tokens=512, temperature=0.7, top_p=0.95
    )


def _max_chunk_size_formula(
    prompt_tokens: int, output_tokens: int, context_length: int
):
    chunk_size = context_length - prompt_tokens - output_tokens
    if chunk_size <= MIN_CHUNK_SIZE:
        raise ValueError(
            (
                f"The max computed chunk size ({chunk_size}) is less than the allowed min size: "
                f"{MIN_CHUNK_SIZE}. Either lower the summary size or increase the context window."
            )
        )
    return chunk_size


@tracer.start_as_current_span("auto_chunk_size_long_desc")
def auto_chunk_size_long_desc(
    llm: LLM, summary_size: int | None = Params.long_description.max_tokens
) -> int:
    if summary_size is None:
        summary_size = 512
    assert summary_size > 0, "Must have positive summary size"
    if llm.is_chat_model:
        prompt = templates.LongDescription.render(
            document_type="longest doc type possible",
            document_content="",
            current_description="",
            llm=llm,
        )
    else:
        prompt = templates.LongDescription.render_instruct(
            document_type="longest doc type possible",
            document_content="",
            current_description="",
        )
    prompt_tokens = llm.num_tokens(prompt) + summary_size
    chunk_size = _max_chunk_size_formula(
        prompt_tokens=prompt_tokens,
        output_tokens=summary_size,
        context_length=llm.context_length,
    )
    return chunk_size


@tracer.start_as_current_span("auto_chunk_size_summarize")
def auto_chunk_size_summarize(llm: LLM, summary_size: int | None = None) -> int:
    if summary_size is None:
        summary_size = Params.summarize.max_tokens
        if summary_size is None:
            raise ValueError(
                "Internal error. Default summarize max_tokens param should be set"
            )
    assert summary_size > 0, "Must have positive summary size"
    if llm.is_chat_model:
        prompt = templates.Summarize.render(passage="", llm=llm)
    else:
        prompt = templates.Summarize.render_instruct(passage="")
    prompt_tokens = llm.num_tokens(prompt) + summary_size
    chunk_size = _max_chunk_size_formula(
        prompt_tokens=prompt_tokens,
        output_tokens=summary_size,
        context_length=llm.context_length,
    )
    return chunk_size


@tracer.start_as_current_span("agent_summary")
async def agent_summary(
    llm: LLM,
    char: str,
    memories: list[Memory],
    questions: list[str] | None = None,
    long_description: str | None = None,
    short_description: str | None = None,
    system_prompt: str | None = None,
    **kwargs,
) -> str:
    if llm.is_chat_model:
        prompt = templates.AgentSummary.render(
            llm=llm,
            char=char,
            memories=memories,
            questions=questions,
            long_description=long_description,
            short_description=short_description,
            system_prompt=system_prompt,
        )
    else:
        prompt = templates.AgentSummary.render_instruct(
            char=char,
            memories=memories,
            long_description=long_description,
            short_description=short_description,
            questions=questions,
        )
    kwargs["template"] = templates.AgentSummary.__name__
    kwargs["subroutine"] = agent_summary.__name__
    r = await llm.agenerate(
        prompt_or_messages=prompt, params=Params.agent_summary, **kwargs
    )
    # (Jonny) the agent summary answers each of the questions, and actually returns
    # a numbered list as output. Parse this. We use \b since it's still fine
    # to split on numbered things inside the text. Just pray we don't have a sentence
    # ending with \d.
    summary = "".join(re.split(r"\b\d\.\s*", r.content))
    return summary.strip()


@tracer.start_as_current_span("long_description_create")
async def long_description_create(
    llm: LLM, short_description: str, docs: list[Document], **kwargs
) -> str:
    """WARNING: this thing could be pretty expensive, it will run ALL documents
    through the LLM. but tests show this is the highest quality, using cached summaries
    doesn't work as well :("""
    current_description = short_description
    chunk_size = auto_chunk_size_long_desc(llm=llm)
    splitter = TokenSplitter(
        tokenizer=getattr(llm, "tokenizer", Tokenizer.from_openai("gpt-3.5-turbo")),
        chunk_size=chunk_size,
        chunk_overlap=32,
    )
    for doc in docs:
        text = doc.content
        chunks = splitter.split(text)
        for i, chunk in enumerate(chunks):
            prompt = templates.LongDescription.render_instruct(
                document_type=doc.type or "character information",
                document_content=chunk,
                current_description=current_description,
            )
            kwargs["template"] = templates.LongDescription.__name__
            kwargs["subroutine"] = long_description_create.__name__
            kwargs["document_id"] = str(doc.id)
            kwargs["chunk_index"] = i
            r = await llm.agenerate(prompt, params=Params.long_description, **kwargs)
            current_description = r.content.strip()
    return current_description


@tracer.start_as_current_span("entity_context_create")
async def entity_context_create(
    llm: LLM,
    char: str,
    entity: str,
    statements: list[Memory],
    system_prompt: str | None = None,
    prev_entity_summary: str | None = None,
    **kwargs,
) -> str:
    if llm.is_chat_model:
        prompt = templates.EntityContextCreate.render(
            llm=llm,
            char=char,
            entity=entity,
            statements=statements,
            system_prompt=system_prompt,
            prev_entity_summary=prev_entity_summary,
        )
    else:
        prompt = templates.EntityContextCreate.render_instruct(
            char=char,
            entity=entity,
            statements=statements,
            prev_entity_summary=prev_entity_summary,
        )
    kwargs["template"] = templates.EntityContextCreate.__name__
    kwargs["subroutine"] = entity_context_create.__name__
    r = await llm.agenerate(
        prompt_or_messages=prompt, params=Params.entity_context_create, **kwargs
    )
    # the questions 1. What is {entity}'s relationship to {char}
    # and 2. How does {char} feel about {entity}? Are baked into the template.
    # the output is not numbered, but commercial LLMs tend to produce numbered outputs
    # so we're being defensive here.
    summary = "".join(re.split(r"\b\d\.\s*", r.content))
    return summary.strip()


@retry(
    stop=stop_after_attempt(MAX_RETRIES),
    wait=wait_random(min=RETRY_MIN, max=RETRY_MAX),
    retry=retry_if_exception_type(OutputParserError),
)
@tracer.start_as_current_span("rate_memory")
async def rate_memory(
    llm: LLM,
    memory: str,
    examples: list[MemoryExample] | None = None,
    system_prompt: str | None = None,
    **kwargs,
) -> int:
    """Returns score on scale of 1-10."""
    if llm.is_chat_model:
        prompt = templates.MemoryRating.render(
            llm=llm,
            memory=memory,
            examples=examples,
            system_prompt=system_prompt,
        )
    else:
        prompt = templates.MemoryRating.render_instruct(
            memory=memory,
            examples=examples,
        )
    kwargs["template"] = templates.MemoryRating.__name__
    kwargs["subroutine"] = rate_memory.__name__
    # FixMe (Jonny): figure out how to properly tell mypy the required type exists here.
    kwargs["retry_attempt"] = rate_memory.retry.statistics["attempt_number"] - 1  # type: ignore
    params = GenerationParams(**templates.MemoryRating.get_constraints(llm=llm))
    r = await llm.agenerate(prompt_or_messages=prompt, params=params, **kwargs)
    try:
        return int(r.content.strip()) + 1
    except ValueError:
        attributes = dict(
            subroutine=kwargs["subroutine"], model=llm.model, model_type=llm.model_type
        )
        output_parsing_exception_meter.add(amount=1, attributes=attributes)

        if isinstance(llm, MockLLM):
            return 4
        err_msg = f"Could not parse output to an integer. Output: {r.content.strip()}"
        logger.error(err_msg)
        raise OutputParserError(err_msg)


@retry(
    stop=stop_after_attempt(MAX_RETRIES),
    wait=wait_random(min=RETRY_MIN, max=RETRY_MAX),
    retry=retry_if_exception_type(OutputParserError),
)
@tracer.start_as_current_span("message_queries_create")
async def message_queries_create(
    llm: LLM,
    char: str,
    short_description: str,
    entity_name: str,
    messages: list[Message],
    agent_summary: str | None = None,
    entity_context_summary: str | None = None,
    num_results: int = 3,
    system_prompt: str | None = None,
    **kwargs,
) -> list[str]:
    """Returns score on scale of 1-10."""
    if llm.is_chat_model:
        prompt = templates.MessageQuery.render(
            llm=llm,
            char=char,
            short_description=short_description,
            agent_summary=agent_summary,
            entity_context_summary=entity_context_summary,
            entity_name=entity_name,
            messages=messages,
            system_prompt=system_prompt,
            num_results=num_results,
        )
    else:
        raise NotImplementedError("Instruct not implemented for MessageQuery template")
    kwargs["template"] = templates.MessageQuery.__name__
    kwargs["subroutine"] = message_queries_create.__name__
    kwargs["retry_attempt"] = (
        message_queries_create.retry.statistics["attempt_number"] - 1  # type: ignore
    )
    r = await llm.agenerate(
        prompt_or_messages=prompt, params=Params.message_queries_create, **kwargs
    )
    # NOTE (Jonny): We're trying to force no extra output like "Sure!" or "Certainly!" by
    # prefilling the first two tokens. We are currently enforcing that these first tokens
    # line up with the templates through the power of thoughts and prayers ^_^
    text = f'["{r.content.strip()}'
    try:
        queries = json.loads(text)
    except json.JSONDecodeError:
        attributes = dict(
            subroutine=kwargs["subroutine"], model=llm.model, model_type=llm.model_type
        )
        output_parsing_exception_meter.add(amount=1, attributes=attributes)
        # if isinstance(llm, MockLLM):
        #     return ["foo", "bar", "baz"]

        # see if we got back a numbered list
        numbered_arr = re.split(r"\b\d\.\s*", text)
        numbered_arr = list(filter(bool, numbered_arr))
        if len(numbered_arr) == num_results:
            return numbered_arr

        # To prevent blocking, we will settle for just returning whatever shit the LLM
        # output. In the controller, we append the last msg too, so the damage is hopefully
        # not that bad.
        err_msg = f"Unable to parse message_query_create output to JSON. Output: {text}"
        logger.error(err_msg)
        if kwargs["retry_attempt"] >= MAX_RETRIES - 1:
            logger.warning("Returning approximate answer.")
            return text.strip().split("\n")
        logger.error(err_msg)
        raise OutputParserError(err_msg)

    # Sometimes we get back valid JSON, but it's not a list, random shit like
    # [{"a":"hello", "b":"world"}]. Use Pydantic to remove these.
    try:
        QueryList(arr=queries)
    except ValidationError as e:
        attributes = dict(
            subroutine=kwargs["subroutine"], model=llm.model, model_type=llm.model_type
        )
        output_parsing_exception_meter.add(amount=1, attributes=attributes)
        raise OutputParserError(e)
    return queries


@tracer.start_as_current_span("question_and_answer")
async def question_and_answer(
    llm: LLM,
    question: str,
    excerpts: list[Excerpt] | None = None,
    system_prompt: str | None = None,
    **kwargs,
) -> str:
    if llm.is_chat_model:
        prompt = templates.QuestionAndAnswer.render(
            llm=llm,
            question=question,
            excerpts=excerpts,
            system_prompt=system_prompt,
        )
    else:
        prompt = templates.QuestionAndAnswer.render_instruct(
            question=question,
            excerpts=excerpts,
        )
    kwargs["template"] = templates.QuestionAndAnswer.__name__
    kwargs["subroutine"] = question_and_answer.__name__
    r = await llm.agenerate(
        prompt_or_messages=prompt, params=Params.question_and_answer, **kwargs
    )
    return r.content.strip()


@retry(
    stop=stop_after_attempt(MAX_RETRIES),
    wait=wait_random(min=RETRY_MIN, max=RETRY_MAX),
    retry=retry_if_exception_type(OutputParserError),
)
@tracer.start_as_current_span("reflection_queries_create")
async def reflection_queries_create(
    llm: LLM,
    memories: list[Memory],
    num_questions: int = 3,
    system_prompt: str | None = None,
    **kwargs,
) -> list[str]:
    """Returns a set of questions to be used for querying memories used in reflection."""
    if llm.is_chat_model:
        prompt = templates.ReflectionQuestions.render(
            llm=llm,
            memories=memories,
            num_questions=num_questions,
            system_prompt=system_prompt,
        )
    else:
        prompt = templates.ReflectionQuestions.render_instruct(
            memories=memories, num_questions=num_questions
        )
    kwargs["template"] = templates.ReflectionQuestions.__name__
    kwargs["subroutine"] = reflection_queries_create.__name__
    kwargs["retry_attempt"] = (
        reflection_queries_create.retry.statistics["attempt_number"] - 1  # type: ignore
    )
    r = await llm.agenerate(
        prompt_or_messages=prompt, params=Params.reflection_queries_create, **kwargs
    )
    text = f'["{r.content.strip()}'
    try:
        queries = json.loads(text)
    except json.JSONDecodeError:
        attributes = dict(
            subroutine=kwargs["subroutine"], model=llm.model, model_type=llm.model_type
        )
        output_parsing_exception_meter.add(amount=1, attributes=attributes)

        if isinstance(llm, MockLLM):
            return ["What do I stand for?", "Where was I?"]

        err_msg = f"Unable to parse reflection_queries_create output ({text}) to JSON."
        logger.error(err_msg)

        # Similar to msg_queries, we just settle for the output and use that as query
        # if we fail enough times
        if kwargs["retry_attempt"] >= MAX_RETRIES - 1:
            logger.error(err_msg + " Returning approximate answer.")
            return text.strip().split("\n")

        raise OutputParserError(err_msg)
    try:
        QueryList(arr=queries)
    except ValidationError as e:
        attributes = dict(
            subroutine=kwargs["subroutine"], model=llm.model, model_type=llm.model_type
        )
        output_parsing_exception_meter.add(amount=1, attributes=attributes)

        raise OutputParserError(e)
    return queries


@retry(
    stop=stop_after_attempt(MAX_RETRIES),
    wait=wait_random(min=RETRY_MIN, max=RETRY_MAX),
    retry=retry_if_exception_type(OutputParserError),
)
@tracer.start_as_current_span("reflections_create")
async def reflections_create(
    llm: LLM,
    memories: list[Memory],
    system_prompt: str | None = None,
    **kwargs,
) -> list[MemoryWithoutRating]:
    """WARNING: This will produce memories that have not been rated for importance!"""
    if llm.is_chat_model:
        prompt = templates.ReflectionInsights.render(
            llm=llm,
            statements=memories,
            system_prompt=system_prompt,
        )
    else:
        prompt = templates.ReflectionInsights.render_instruct(
            statements=memories,
        )
    kwargs["template"] = templates.ReflectionInsights.__name__
    kwargs["subroutine"] = reflections_create.__name__
    kwargs["retry_attempt"] = reflections_create.retry.statistics["attempt_number"] - 1  # type: ignore

    index_to_memory = {i + 1: m for i, m in enumerate(memories)}

    r = await llm.agenerate(
        prompt_or_messages=prompt, params=Params.reflection_create, **kwargs
    )

    # NOTE (Jonny): More thoughts and prayers here to ensure it aligns with the templates ^_^
    text = '[{"insight":' + r.content
    try:
        data = json.loads(text)
        refls = [ReflectionItem(**x) for x in data]
    except json.JSONDecodeError:
        if isinstance(llm, MockLLM):
            refls = [
                ReflectionItem(insight="this is an insight", memories=[1]),
                ReflectionItem(insight="this is also an insight", memories=[1, 2]),
            ]
        else:
            attributes = dict(
                subroutine=kwargs["subroutine"],
                model=llm.model,
                model_type=llm.model_type,
            )
            output_parsing_exception_meter.add(amount=1, attributes=attributes)

            err_msg = (
                f"Unable to convert reflections_create output to JSON. Output: {text}"
            )
            logger.error(err_msg)
            raise OutputParserError(err_msg)

    reflections: list[MemoryWithoutRating] = []
    for x in refls:
        try:
            child_indexes = x.memories
            children = [index_to_memory[z] for z in child_indexes]
        except IndexError as e:
            attributes = dict(
                subroutine=kwargs["subroutine"],
                model=llm.model,
                model_type=llm.model_type,
            )
            output_parsing_exception_meter.add(amount=1, attributes=attributes)
            err_msg = (
                "Parsing failure. Reflection memory dependencies do not point "
                f"to valid indexes: {e}"
            )
            logger.error(err_msg)
            raise OutputParserError(err_msg)
        except Exception as e:
            attributes = dict(
                subroutine=kwargs["subroutine"],
                model=llm.model,
                model_type=llm.model_type,
            )
            output_parsing_exception_meter.add(amount=1, attributes=attributes)

            err_msg = f"Unknown parsing error. {e}"
            logger.error(err_msg)
            raise OutputParserError(err_msg)
        depth = max(c.depth for c in children) + 1
        child_ids = [c.id for c in children]
        m = MemoryWithoutRating(
            content=x.insight,
            depth=depth,
            child_ids=child_ids,
        )
        reflections.append(m)
    return reflections


@tracer.start_as_current_span("summarize")
async def summarize(
    llm: LLM,
    passage: str,
    system_prompt: str | None = None,
    **kwargs,
) -> str:
    if llm.is_chat_model:
        prompt = templates.Summarize.render(
            llm=llm,
            passage=passage,
            system_prompt=system_prompt,
        )
    else:
        prompt = templates.Summarize.render_instruct(
            passage=passage,
        )
    kwargs["template"] = templates.Summarize.__name__
    kwargs["subroutine"] = summarize.__name__
    r = await llm.agenerate(
        prompt_or_messages=prompt, params=Params.summarize, **kwargs
    )
    return r.content.strip()


@tracer.start_as_current_span("online_summarize")
async def online_summarize(
    llm: LLM,
    nodes: list[Node],
    system_prompt: str | None = None,
    **kwargs,
) -> list[LLMResponse]:
    """WARNING (Jonny): this is an inplace operation (it modifies attributes on the nodes, intentionally)
    and also potentially very expensive if there are many nodes! It's very similar to LongDescription, but
    has no auto chunk size in place to ensure you use the biggest nodes possible. I'm going to add an input
    check to make sure you don't accidentally run this lol. The output isn't really needed, it's just for sanity
    """
    if not isinstance(llm, MockLLM):
        msg = "Are you sure you want to online summarize with {len(nodes)} nodes? (y/n)"
        assert input(msg) == "y", "Fuck that noise"
    kwargs["template"] = templates.Summarize.__name__
    kwargs["subroutine"] = online_summarize.__name__
    calls: list[LLMResponse] = []
    prev_summary = "No summary yet."
    for i, node in enumerate(nodes):
        kwargs["group"] = f"{i + 1}/{len(nodes)}"
        if llm.is_chat_model:
            prompt = templates.OnlineSummarize.render(
                llm=llm,
                passage=node.content,
                prev_summary=prev_summary,
                system_prompt=system_prompt,
            )
        else:
            prompt = templates.OnlineSummarize.render_instruct(
                passage=node.content.strip(),
                prev_summary=prev_summary,
            )
        r = await llm.agenerate(
            prompt_or_messages=prompt, params=Params.online_summarize, **kwargs
        )
        node.context = prev_summary = r.content.strip()
        calls.append(r)
    return calls


@tracer.start_as_current_span("generate_zero_memory_message")
async def generate_zero_memory_message(
    llm: LLM,
    char: str,
    user_name: str,
    short_description: str,
    long_description: str,
    messages: list[Message],
    monologues: list[Monologue] | None = None,
    facts: list[str] | None = None,
    use_timestamps: bool = False,
    **kwargs,
) -> str:
    if not llm.is_chat_model:
        raise NotImplementedError("Instruct for message gen not supported yet.")
    prompt = templates.ZeroMemoryMessage.render(
        llm=llm,
        char=char,
        user_name=user_name,
        short_description=short_description,
        long_description=long_description,
        messages=messages,
        monologues=monologues,
        facts=facts,
        use_timestamps=use_timestamps,
    )
    kwargs["template"] = templates.ZeroMemoryMessage.__name__
    kwargs["subroutine"] = generate_long_term_memory_message.__name__
    r = await llm.agenerate(
        prompt_or_messages=prompt, params=Params.generate_zero_memory_message, **kwargs
    )
    return r.content.strip()


@tracer.start_as_current_span("generate_long_term_memory_message")
async def generate_long_term_memory_message(
    llm: LLM,
    char: str,
    user_name: str,
    short_description: str,
    long_description: str,
    messages: list[Message],
    monologues: list[Monologue] | None = None,
    facts: list[str] | None = None,
    memories: list[Memory] | None = None,
    agent_summary: str | None = None,
    entity_context_summary: str | None = None,
    use_timestamps: bool = False,
    **kwargs,
) -> str:
    if not llm.is_chat_model:
        raise NotImplementedError("Instruct for message gen not supported yet.")
    prompt = templates.LongTermMemoryMessage.render(
        llm=llm,
        char=char,
        user_name=user_name,
        short_description=short_description,
        long_description=long_description,
        messages=messages,
        monologues=monologues,
        facts=facts,
        memories=memories,
        agent_summary=agent_summary,
        entity_context_summary=entity_context_summary,
        use_timestamps=use_timestamps,
    )
    kwargs["template"] = templates.LongTermMemoryMessage.__name__
    kwargs["subroutine"] = generate_long_term_memory_message.__name__
    r = await llm.agenerate(
        prompt_or_messages=prompt,
        params=Params.generate_long_term_memory_message,
        **kwargs,
    )
    return r.content.strip()
