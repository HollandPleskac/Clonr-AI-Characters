from pydantic import BaseModel

from clonr.llms import LLM

from ._env import env


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
Include key points, important details, and salient information. \
Do not write anything other than the summary.\
\
{#### EXAMPLES ####}\
{% if (examples) -%}
{{ llm.user_end }}
{% for example in examples %}
{%- if (loop.first) -%}{{ llm.user_start }}{%- endif %}
--- Example {{ loop.index }} ---
{{- llm.user_end }}
{{ llm.user_start -}}
Passage: {{ example.passage }}
{{- llm.user_end }}

{{ llm.assistant_start -}}
Summary: {{ example.summary }}
{{- llm.assistant_end }}
{%- if (loop.last) %}

{% endif -%}
{{- llm.user_start }}
{%- endfor -%}
{%- endif -%}
\
{#### TASK #####}\
--- Task ---
Passage: {{ passage }}
{{- llm.user_end }}

{#### ASSISTANT START ####}\
{{ llm.assistant_start -}}\
Summary:\
"""
    )

    guidance_template = """\
{{#system~}}
{{ system_prompt }}
{{~/system}}

{{~! EXPLAIN THE SUMMARIZATION TASK ~}}
{{#user~}}
Given a passage of text, write a summary of the passage. \
Include key points, important details, and salient information. \
Do not write anything other than the summary.\
{{~#if examples}}{{/user}}{{/if}}

{{~! EXPLAIN THE SUMMARIZATION TASK ~}}
{{~#each examples}}
{{#user~}}
Passage: {{this.passage}}
{{~/user}}

{{#assistant~}}
Summary: {{this.summary}}
{{~/assistant}}
{{~/each}}
{{~#if examples}}{{#user}}{{/if}}

{{~! TASK ~}}
--- Task ---
Passage: {{passage}}
{{~/user}}

{{~! GENERATE SUMMARY}}\
{{#assistant~}}
Summary: {{gen "summary" temperature=TEMPERATURE max_tokens=MAX_TOKENS}}
{{~/assistant}}\
"""

    @classmethod
    def render(
        cls,
        llm: LLM,
        passage: str,
        system_prompt: str | None = None,
        examples: list[SummaryExample] | None = None,
    ) -> str:
        if system_prompt is None:
            system_prompt = llm.default_system_prompt
        if examples is None:
            examples = []
        return cls.template.render(
            llm=llm,
            passage=passage,
            system_prompt=system_prompt,
            examples=examples,
        )

    @classmethod
    def guidance_render(
        cls,
        temperature: float = 0.7,
        max_tokens: int = 256,
    ) -> str:
        return cls.guidance_template.replace(
            "TEMPERATURE", str(round(temperature, 2))
        ).replace("MAX_TOKENS", str(int(max_tokens)))


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
{% if (examples) -%}
{{ llm.user_end }}
{% for example in examples %}
{%- if (loop.first) -%}{{ llm.user_start }}{%- endif %}
--- Example {{ loop.index }} ---
{{- llm.user_end }}
{{ llm.user_start -}}
Context: {{ example.context }}
Passage: {{ example.passage }}
{{- llm.user_end }}

{{ llm.assistant_start -}}
Summary: {{ example.summary }}
{{- llm.assistant_end }}
{%- if (loop.last) %}

{% endif -%}
{{- llm.user_start }}
{%- endfor -%}
{%- endif -%}
\
{#### TASK #####}\
--- Task ---
Context: {{ context }}
Passage: {{ passage }}
{{- llm.user_end }}

{#### ASSISTANT START ####}\
{{ llm.assistant_start -}}\
Summary:\
"""
    )

    guidance_template = """\
{{#system~}}
{{ system_prompt }}
{{~/system}}

{{~! EXPLAIN THE SUMMARIZATION TASK ~}}
{{#user~}}
Given a passage of text, write a summary of the passage. \
Include key points, important details, and salient information. \
Do not write anything other than the summary.\
{{~#if examples}}{{/user}}{{/if}}

{{~! EXPLAIN THE SUMMARIZATION TASK ~}}
{{~#each examples}}
{{#user~}}
Context: {{this.context}}
Passage: {{this.passage}}
{{~/user}}

{{#assistant~}}
Summary: {{this.summary}}
{{~/assistant}}
{{~/each}}
{{~#if examples}}{{#user}}{{/if}}

{{~! TASK ~}}
--- Task ---
Context: {{context}}
Passage: {{passage}}
{{~/user}}

{{~! GENERATE SUMMARY}}\
{{#assistant~}}
Summary: {{gen "summary" temperature=TEMPERATURE max_tokens=MAX_TOKENS}}
{{~/assistant}}\
"""

    @classmethod
    def render(
        cls,
        llm: LLM,
        context: str,
        passage: str,
        system_prompt: str | None = None,
        examples: list[SummaryExampleWithContext] | None = None,
    ) -> str:
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

    @classmethod
    def guidance_render(
        cls,
        temperature: float = 0.7,
        max_tokens: int = 256,
    ) -> str:
        return cls.guidance_template.replace(
            "TEMPERATURE", str(round(temperature, 2))
        ).replace("MAX_TOKENS", str(int(max_tokens)))
