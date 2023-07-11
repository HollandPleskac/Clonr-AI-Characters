from clonr.data_structures import Memory
from clonr.llms import LLM
from clonr.templates.base import Template, env


# TODO (Jonny): test that these work
# Retrieve most salient questions for reflection
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
{{loop.index}}. {{memory}}
{%- endfor %} 
---
Given only the information above, what are the 3 most salient high-level \
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
{{loop.index}}. {{memory}}
{%- endfor %} 
---

Given only the information above, what are the 3 most salient high-level \
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
        memories: list[str] | list[Memory],
        system_prompt: str | None = None,
    ):
        if system_prompt is None:
            system_prompt = llm.default_system_prompt
        memories_ = [m if isinstance(m, str) else m.to_str() for m in memories]
        return cls.chat_template.render(
            llm=llm, system_prompt=system_prompt, memories=memories_
        )

    @classmethod
    def render_instruct(
        cls,
        memories: str,
    ):
        memories_ = [m if isinstance(m, str) else m.to_str() for m in memories]
        return cls.instruct_template.render(memories=memories_)


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
{%- endfor %} 
---

What 5 high-level insights can you infer from the above \
statements of relevant memories, thoughts, and observations? \
Return your answer as a JSON list.
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
{% for statement in statements -%}
{{loop.index}}. {{statement}}
{%- endfor %} 
---

What 5 high-level insights can you infer from the above \
statements of relevant memories, thoughts, and observations? \
Return your answer as a JSON list.

### Response:
["\
"""
    )

    @classmethod
    def render(
        cls,
        llm: LLM,
        statements: list[str] | list[Memory],
        system_prompt: str | None = None,
    ):
        if system_prompt is None:
            system_prompt = llm.default_system_prompt
        statements = [s if isinstance(s, str) else s.content for s in statements]
        return cls.template.render(
            llm=llm, system_prompt=system_prompt, statements=statements
        )

    @classmethod
    def render_instruct(
        cls,
        statements: list[str] | list[Memory],
    ):
        statements = [s if isinstance(s, str) else s.content for s in statements]
        return cls.instruct_template.render(statements=statements)
