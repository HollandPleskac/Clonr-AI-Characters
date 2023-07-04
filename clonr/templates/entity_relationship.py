from clonr.llms import LLM
from clonr.templates.base import Template, env


# TODO (Jonny): test that these work
# Retrieve most salient questions for reflection
class EntityContextCreate(Template):
    chat_template = env.from_string(
        """\
{{ llm.system_start -}}
{{ system_prompt }}
{{- llm.system_end }}

{{ llm.user_start -}}
Using the following statements (enclosed with ---) of recent memories, thoughts, \
and observations, answer the question that follows.
---
{% for stmt in statements -%}
{{loop.index}}. {{stmt}}
{%- endfor %} 
---

What is {{char}}'s relationship to {{entity}}, how does {{char}} feel about {{entity}}, \
and what is {{entity}}'s current status? Use ony the statements provided above and not prior knowledge. \
Your answer should be concise yet contain all of the necessary information to provide a full answer.
{{- llm.user_end }}

{{ llm.assistant_start -}}
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
{% for stmt in statements -%}
{{loop.index}}. {{stmt}}
{%- endfor %} 
---

What is {{char}}'s relationship to {{entity}}, how does {{char}} feel about {{entity}}, \
and what is {{entity}}'s current status? Use ony the statements provided above and not prior knowledge. \
Your answer should be concise yet contain all of the necessary information to provide a full answer.

### Response:
"""
    )

    @classmethod
    def get_vectordb_queries(cls, char: str, entity: str) -> list[str]:
        q1 = f"What is {char}'s relationship to {entity}"
        q2 = f"What is {entity}'s current status?"
        return [q1, q2]

    @classmethod
    def render(
        cls,
        llm: LLM,
        statements: list[str],
        system_prompt: str | None = None,
    ):
        if system_prompt is None:
            system_prompt = llm.default_system_prompt
        return cls.chat_template.render(
            llm=llm, system_prompt=system_prompt, statements=statements
        )

    @classmethod
    def render_chat(
        cls,
        statements: list[str],
    ):
        return cls.instruct_template.render(statements=statements)
