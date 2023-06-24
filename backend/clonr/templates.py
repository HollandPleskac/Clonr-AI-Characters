import jinja2
from clonr.llms import LLM
from pydantic import BaseModel

env = jinja2.Environment(
    enable_async=False, autoescape=False, undefined=jinja2.StrictUndefined
)


class BasicChat:
    template = env.from_string(
        """\
{{ llm.system_start -}}
{% if (system_prompt) -%}
{{ system_prompt -}}
{%- else -%}
{{ llm.default_system_prompt -}}
{%- endif %}
{{- llm.system_end }}

{{ llm.user_start -}}
{{ user_prompt }}
{{- llm.user_end }}

{{ llm.assistant_start -}}\
"""
    )

    @classmethod
    def render(cls, llm: LLM, user_prompt: str, system_prompt: str | None = None):
        return cls.template.render(
            llm=llm, user_prompt=user_prompt, system_prompt=system_prompt
        )


class SummaryExample(BaseModel):
    passage: str
    summary: str


class SummaryExampleWithContext(SummaryExample):
    context: str


class Summarize:
    template = env.from_string(
        """\
{#### SYSTEM PROMPT ####}\
{{ llm.system_start -}}
{{ system_prompt }}
{{- llm.system_end }}

{#### USER START ####}\
{{ llm.user_start -}}\

{#### EXPLAIN THE SUMMARIZATION TASK ####}\
Given a passage of text, write a summary of the passage. \
Include key points, important details, and salient information.
\
{#### EXAMPLES ####}
{%- for example in examples -%}
fuck
{%- endfor %}
\
\
{{- llm.user_end }}

{{ llm.assistant_start -}}\
"""
    )

    @classmethod
    def render(
        cls,
        llm: LLM,
        passage: str,
        system_prompt: str | None = None,
        examples: list[SummaryExample] | None = None,
    ):
        if system_prompt is None:
            system_prompt = llm.default_system_prompt
        return cls.template.render(
            llm=llm,
            system_prompt=system_prompt,
            examples=examples or [],
        )


class SummarizeWithContext:
    template = env.from_string(
        """\
{#### SYSTEM PROMPT ####}\
{{ llm.system_start -}}
{{ system_prompt }}
{{- llm.system_end }}

{#### USER START ####}\
{{ llm.user_start -}}\

{#### EXPLAIN THE SUMMARIZATION TASK ####}\
Given a passage of text and a paragraph of context for that passage, \
write a summary of the passage. Include key points, important details, and \
make use of the context where necessary. \
Do not write anything other than the summary.\
\
{#### EXAMPLES ####}\
{%- for example in examples %}

--- Example {{ loop.index }} ---
Context: {{ example.context }}
Passage: {{ example.passage }}
Summary: {{ example.summary }}
{%- endfor %}

{### TASK ####}\
\
{{- llm.user_end }}
\
{{ llm.assistant_start -}}\
Context: {{ context }}
Passage: {{ passage }}
Summary:\
"""
    )

    @classmethod
    def render(
        cls,
        llm: LLM,
        context: str,
        passage: str,
        system_prompt: str | None = None,
        examples: list[dict] | None = None,
    ):
        if system_prompt is None:
            system_prompt = llm.default_system_prompt
        if examples is None:
            examples = []
        return cls.template.render(
            llm=llm,
            context=context,
            passage=passage,
            system_prompt=system_prompt,
            examples=examples,
        )

    # @classmethod
    # def dummy_render(cls, *args)


# Given an observation, rate the significance of it
class Memory:
    template = env.from_string(
        """\
{#### SYSTEM PROMPT ####}\
{{ llm.system_start -}}
{{ system_prompt }}
{{- llm.system_end }}

{#### USER START ####}\
{{ llm.user_start -}}\

{#### EXPLAIN THE MEMORY TASK ####}\
Given the following memory, rate the significance of the memory. \
Use a scale of 1 to 10, where 1 is purely mundane (e.g., brushing teeth, making bed) and 10 is extremely poignant (e.g., a break up, college acceptance). \
Rate the likely poignancy of the following piece of memory. \
Respond with a single integer.
\
{#### MEMORY ####}
Memory: {{ memory }}
\
{{- llm.user_end }}

{{ llm.assistant_start -}}\
"""
    )

    @classmethod
    def render(
        cls,
        llm: LLM,
        memory: str,
        system_prompt: str | None = None,
    ):
        if system_prompt is None:
            system_prompt = llm.default_system_prompt
        return cls.template.render(llm=llm, system_prompt=system_prompt, memory=memory)


# Retrieve most salient questions for reflection
class ReflectionRetrieval:
    template = env.from_string(
        """\
{#### SYSTEM PROMPT ####}\
{{ llm.system_start -}}
{{ system_prompt }}
{{- llm.system_end }}

{#### USER START ####}\
{{ llm.user_start -}}\

{#### RECENT MEMORIES ####}
Recent memories: {{ recent_memories }} 
\

{#### EXPLAIN THE REFLECTION RETRIEVAL TASK ####}\
Given only the information above on recent memories, what are 3 most salient high-level questions we can answer about the subjects in the statements? \
\

{{- llm.user_end }}

{{ llm.assistant_start -}}\
"""
    )

    @classmethod
    def render(
        cls,
        llm: LLM,
        memories: str,
        system_prompt: str | None = None,
    ):
        if system_prompt is None:
            system_prompt = llm.default_system_prompt
        return cls.template.render(
            llm=llm, system_prompt=system_prompt, memories=memories
        )


# Generate actual reflections / insights based on retrieved salient memories
class ReflectionGeneration:
    template = env.from_string(
        """\
{#### SYSTEM PROMPT ####}\
{{ llm.system_start -}}
{{ system_prompt }}
{{- llm.system_end }}

{#### USER START ####}\
{{ llm.user_start -}}\

{#### RELEVANT MEMORIES ####}
Relevant memories: {{ relevant_memories }}
\

{#### EXPLAIN THE REFLECTION GENERATION TASK ####}\
What 5 high-level insights can you infer from the above statements of relevant memories? \
\

{{- llm.user_end }}

{{ llm.assistant_start -}}\
"""
    )

    @classmethod
    def render(
        cls,
        llm: LLM,
        relevant_memories: str,
        system_prompt: str | None = None,
    ):
        if system_prompt is None:
            system_prompt = llm.default_system_prompt
        return cls.template.render(
            llm=llm, system_prompt=system_prompt, relevant_memories=relevant_memories
        )

    # class Instruct:
    """\
Below is an instruction that describes a task. Write a response that appropriately completes the request.

### Instruction:
{instruction}

### Response:"""
