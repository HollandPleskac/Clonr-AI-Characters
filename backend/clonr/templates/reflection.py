from clonr.data_structures import Memory
from clonr.llms import LLM
from clonr.templates.base import Template, env


# TODO (Jonny): test that these work
# Retrieve most salient questions for reflection
# NOTE (Jonny): we're not using timestamps here. They're fucking expensive and probably don't add
# that much to the output quality (a penalty of 18 tokens per memory!)
class ReflectionQuestions(Template):
    chat_template = env.from_string(
        """\
{{ llm.system_start -}}
{{ system_prompt }}
{{- llm.system_end }}

{{ llm.user_start -}}
Using the following statements (enclosed with ---) of recent memories, thoughts, \
and observations, answer the question that follows.
---
{% for memory in memories -%}
{{loop.index}}. {{memory.content}}
{%- endfor %} 
---
Given only the information above, what are the {{num_questions}} most salient high-level \
questions that we can answer about the subjects in the above statements? \
Return your response as a JSON list.
{{- llm.user_end }}

{{ llm.assistant_start -}}
["\
{{- llm.assistant_end -}}
"""
    )

    instruct_template = env.from_string(
        """\
Below is an instruction that describes a task. Write a response that \
appropriately completes the request

### Instruction: 
Using the following statements (enclosed with ---) of recent memories, thoughts, \
and observations, answer the question that follows.
---
{% for memory in memories -%}
{{loop.index}}. {{memory.content}}
{%- endfor %} 
---

Given only the information above, what are the {{num_questions}} most salient high-level \
questions that we can answer about the subjects in the above statements? \
Return your response as a JSON list.

### Response:
["\
"""
    )

    @classmethod
    def render(
        cls,
        llm: LLM,
        memories: list[Memory],
        num_questions: int = 3,
        system_prompt: str | None = None,
    ):
        if system_prompt is None:
            system_prompt = llm.default_system_prompt
        # it falls on the caller to sort memories chronologically
        return cls.chat_template.render(
            llm=llm,
            system_prompt=system_prompt,
            memories=memories,
            num_questions=num_questions,
        )

    @classmethod
    def render_instruct(
        cls,
        memories: list[Memory],
        num_questions: int = 3,
    ):
        memories = sorted(memories, key=lambda x: x.timestamp)
        return cls.instruct_template.render(
            memories=memories, num_questions=num_questions
        )


# Generate actual reflections / insights based on retrieved salient memories
class ReflectionInsights(Template):
    template = env.from_string(
        """\
{{ llm.system_start -}}
{{ system_prompt }}
{{- llm.system_end }}

{{ llm.user_start -}}
Using the following statements (enclosed with ---) of recent memories, thoughts, \
and observations, answer the question that follows.
---
{% for statement in statements -%}
{{loop.index}}. {{statement}}
{%- if not loop.last %}
{% endif -%} 
{%- endfor %} 
---

What {{num_reflections}} high-level insights can you infer from the above \
statements of relevant memories, thoughts, and observations? \
For each insight, provide a list of memories that were used to form the insight. \
Return your answer as a list of JSON objects. For example, if the insight "foo bar" \
depends on memories 2, 4, and 5, then the correct JSON format would be:
{"insight":"foo bar", "memories":[2, 4, 5]}.
{{- llm.user_end }}

{{ llm.assistant_start -}}
[{"insight":\
{{- llm.assistant_end -}}
"""
    )

    instruct_template = env.from_string(
        """\
Below is an instruction that describes a task. Write a response that \
appropriately completes the request

### Instruction: 
Using the following statements (enclosed with ---) of recent memories, thoughts, \
and observations, answer the question that follows.
---
{% for statement in statements -%}
{{loop.index}}. {{statement}}
{%- if not loop.last %}
{% endif -%} 
{%- endfor %} 
---

What {{num_reflections}} high-level insights can you infer from the above \
statements of relevant memories, thoughts, and observations? \
For each insight, provide a list of memories that were used to form the insight. \
Return your answer as a list of JSON objects. For example, if the insight "foo bar" \
depends on memories 2, 4, and 5, then the correct JSON format would be:
{"insight":"foo bar", "memories":[2, 4, 5]}.

### Response:
[{"insight":\
"""
    )

    @classmethod
    def render(
        cls,
        llm: LLM,
        statements: list[str] | list[Memory],
        num_reflections: int = 5,
        system_prompt: str | None = None,
    ):
        if system_prompt is None:
            system_prompt = llm.default_system_prompt
        statements = [s if isinstance(s, str) else s.content for s in statements]
        return cls.template.render(
            llm=llm,
            system_prompt=system_prompt,
            statements=statements,
            num_reflections=num_reflections,
        )

    @classmethod
    def render_instruct(
        cls,
        statements: list[str] | list[Memory],
        num_reflections: int = 5,
    ):
        statements = [s if isinstance(s, str) else s.content for s in statements]
        return cls.instruct_template.render(
            statements=statements, num_reflections=num_reflections
        )
