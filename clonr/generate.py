import inspect
import json
import logging
import uuid

from loguru import logger
from tenacity import after_log, before_log, retry, stop_after_attempt, wait_random

from clonr import templates
from clonr.data_structures import Document, Memory, Message, Node
from clonr.llms import LLM, GenerationParams, LLMResponse, MockLLM, OpenAI
from clonr.templates.memory import MemoryExample
from clonr.templates.qa import Excerpt
from clonr.text_splitters import TokenSplitter
from clonr.tokenizer import Tokenizer

MAX_RETRIES = 3
RETRY_MIN = 1e-3
RETRY_MAX = 1e-2
MIN_CHUNK_SIZE = 256


class OutputParserError(Exception):
    pass


class Params:
    agent_summary = GenerationParams(
        max_tokens=768, top_p=0.95, presence_penalty=0.3, temperature=0.6
    )
    long_description = GenerationParams(max_tokens=512, top_p=0.95, temperature=0.5)
    entity_context_create = GenerationParams(
        max_tokens=512, top_p=0.95, temperature=0.5
    )
    rate_memory = None  # these are LLM specific and determined dynamically to make sure we get ints out!
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


def auto_chunk_size_long_desc(
    llm: LLM, summary_size: int = Params.long_description.max_tokens
) -> int:
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


def auto_chunk_size_summarize(
    llm: LLM, summary_size: int = Params.summarize.max_tokens
) -> int:
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


async def agent_summary(
    llm: OpenAI,
    char: str,
    memories: list[str] | list[Memory],
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
    kwargs["subroutine"] = kwargs.get(
        "subroutine", inspect.currentframe().f_code.co_name
    )
    r = await llm.agenerate(
        prompt_or_messages=prompt, params=Params.agent_summary, **kwargs
    )
    return r.content.lstrip()


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
            kwargs["subroutine"] = kwargs.get(
                "subroutine", inspect.currentframe().f_code.co_name
            )
            kwargs["document_id"] = str(doc.id)
            kwargs["chunk_index"] = i
            r = await llm.agenerate(prompt, params=Params.long_description, **kwargs)
            current_description = r.content.strip()
    return current_description


async def entity_context_create(
    llm: LLM,
    char: str,
    entity: str,
    statements: list[str],
    system_prompt: str | None = None,
    **kwargs,
) -> str:
    if llm.is_chat_model:
        prompt = templates.EntityContextCreate.render(
            llm=llm,
            char=char,
            entity=entity,
            statements=statements,
            system_prompt=system_prompt,
        )
    else:
        prompt = templates.EntityContextCreate.render_instruct(
            char=char,
            entity=entity,
            statements=statements,
        )
    kwargs["template"] = templates.EntityContextCreate.__name__
    kwargs["subroutine"] = kwargs.get(
        "subroutine", inspect.currentframe().f_code.co_name
    )
    r = await llm.agenerate(
        prompt_or_messages=prompt, params=Params.entity_context_create, **kwargs
    )
    return r.content.strip()


@retry(
    stop=stop_after_attempt(MAX_RETRIES),
    wait=wait_random(min=RETRY_MIN, max=RETRY_MAX),
    before=before_log(logger, logging.INFO),
    after=after_log(logger, logging.WARN),
)
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
    kwargs["subroutine"] = kwargs.get(
        "subroutine", inspect.currentframe().f_code.co_name
    )
    kwargs["retry_attempt"] = rate_memory.retry.statistics["attempt_number"]
    params = GenerationParams(**templates.MemoryRating.get_constraints(llm=llm))
    r = await llm.agenerate(prompt_or_messages=prompt, params=params, **kwargs)
    try:
        return int(r.content.strip()) + 1
    except ValueError:
        raise OutputParserError(
            f"Unable to convert output ({r.content}) to an integer."
        )


@retry(
    stop=stop_after_attempt(MAX_RETRIES),
    wait=wait_random(min=RETRY_MIN, max=RETRY_MAX),
    before=before_log(logger, logging.INFO),
    after=after_log(logger, logging.WARN),
)
async def message_queries_create(
    llm: LLM,
    char: str,
    short_description: str,
    agent_summary: str,
    entity_context_summary: str,
    entity_name: str,
    messages: list[str] | list[Message],
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
        )
    else:
        prompt = templates.MessageQuery.render_instruct(
            char=char,
            short_description=short_description,
            agent_summary=agent_summary,
            entity_context_summary=entity_context_summary,
            entity_name=entity_name,
            messages=messages,
        )
    kwargs["template"] = templates.MessageQuery.__name__
    kwargs["subroutine"] = kwargs.get(
        "subroutine", inspect.currentframe().f_code.co_name
    )
    kwargs["retry_attempt"] = rate_memory.retry.statistics["attempt_number"]
    r = await llm.agenerate(
        prompt_or_messages=prompt, params=Params.message_queries_create, **kwargs
    )
    # NOTE (Jonny): no way to really enforce this lines up with the templates except
    # for thoughts and prayers ^_^
    text = f'["{r.content.strip()}'
    try:
        queries = json.loads(text)
    except json.JSONDecodeError:
        raise OutputParserError(f"Unable to convert output ({text}) to JSON.")
    return queries


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
    kwargs["subroutine"] = kwargs.get(
        "subroutine", inspect.currentframe().f_code.co_name
    )
    r = await llm.agenerate(
        prompt_or_messages=prompt, params=Params.question_and_answer, **kwargs
    )
    return r.content.strip()


@retry(
    stop=stop_after_attempt(MAX_RETRIES),
    wait=wait_random(min=RETRY_MIN, max=RETRY_MAX),
    before=before_log(logger, logging.INFO),
    after=after_log(logger, logging.WARN),
)
async def reflection_queries_create(
    llm: LLM,
    memories: list[Memory],
    system_prompt: str | None = None,
    **kwargs,
) -> list[str]:
    """Returns a set of questions to be used for querying memories used in reflection."""
    if llm.is_chat_model:
        prompt = templates.ReflectionQuestions.render(
            llm=llm,
            memories=memories,
            system_prompt=system_prompt,
        )
    else:
        prompt = templates.ReflectionQuestions.render_instruct(memories=memories)
    kwargs["template"] = templates.ReflectionQuestions.__name__
    kwargs["subroutine"] = kwargs.get("subroutine", "reflections")
    kwargs["retry_attempt"] = rate_memory.retry.statistics["attempt_number"]
    r = await llm.agenerate(
        prompt_or_messages=prompt, params=Params.reflection_queries_create, **kwargs
    )
    text = f'["{r.content.strip()}'
    try:
        queries = json.loads(text)
    except json.JSONDecodeError:
        raise OutputParserError(f"Unable to convert output ({text}) to JSON.")
    return queries


@retry(
    stop=stop_after_attempt(MAX_RETRIES),
    wait=wait_random(min=RETRY_MIN, max=RETRY_MAX),
    before=before_log(logger, logging.INFO),
    after=after_log(logger, logging.WARN),
)
async def reflection_create(
    llm: LLM,
    statements: list[str],
    system_prompt: str | None = None,
    **kwargs,
) -> list[str]:
    if llm.is_chat_model:
        prompt = templates.ReflectionInsights.render(
            llm=llm,
            statements=statements,
            system_prompt=system_prompt,
        )
    else:
        prompt = templates.ReflectionInsights.render_instruct(
            statements=statements,
        )
    kwargs["template"] = templates.ReflectionInsights.__name__
    kwargs["subroutine"] = kwargs.get("subroutine", "reflections")
    r = await llm.agenerate(
        prompt_or_messages=prompt, params=Params.reflection_create, **kwargs
    )
    text = f'["{r.content.strip()}'
    try:
        queries = json.loads(text)
    except json.JSONDecodeError:
        raise OutputParserError(f"Unable to convert output ({text}) to JSON.")
    return queries


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
    kwargs["subroutine"] = kwargs.get(
        "subroutine", inspect.currentframe().f_code.co_name
    )
    r = await llm.agenerate(
        prompt_or_messages=prompt, params=Params.summarize, **kwargs
    )
    return r.content.strip()


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
    kwargs["subroutine"] = kwargs.get(
        "subroutine", inspect.currentframe().f_code.co_name
    )
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
