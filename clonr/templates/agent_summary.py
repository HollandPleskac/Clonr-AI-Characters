from clonr.llms import LLM
from clonr.templates.base import Template, env


# TODO: test this
class AgentSumary(Template):
    chat_template = env.from_string(
        """\
{{ llm.system_start -}}
{{ system_prompt }}
{{- llm.system_end }}

{{ llm.user_start -}}
You are answering some questions about {{char}}. Here is a long description for the {{char}} innate traits that do not change easily: \
{{long_description}}

Write answers for the following three questions and relevant memories (enclosed with ---). \

Question one: how would one describe {{char}}’s core characteristics given the following?
---
{% for characteristic_memory in characteristic_memories -%}
{{loop.index}}. {{characteristic_memory}}
{%- endfor %} 
---

Question two: how would one describe {{char}}’s current daily occupation?
---
{% for occupation_memory in occupation_memories -%}
{{loop.index}}. {{occupation_memory}}
{%- endfor %}
---

Question three: how would one describe {{char}}’s feeling about the recent progress in life?
---
{% for feeling_memory in feeling_memories -%}
{{loop.index}}. {{feeling_memory}}
{%- endfor %}
---

Return your answers as a numbered list, 1-3, for each of the above corresponding questions.

{{- llm.user_end }}

{{ llm.assistant_start -}}
1.\
{{- llm.assistant_end -}}
"""
    )

    instruct_template = env.from_string(
        """\
Below is an instruction that describes a task. Write a response that \
appropriately completes the request

### Instruction: 
You are answering some questions about {{char}}. Here is a long description for the {{char}} innate traits that do not change easily: \
{{long_description}}

Write answers for the following three questions and relevant memories (enclosed with ---). \

Question one: how would one describe {{char}}’s core characteristics given the following?
---
{% for characteristic_memory in characteristic_memories -%}
{{loop.index}}. {{characteristic_memory}}
{%- endfor %} 
---

Question two: how would one describe {{char}}’s current daily occupation?
---
{% for occupation_memory in occupation_memories -%}
{{loop.index}}. {{occupation_memory}}
{%- endfor %}
---

Question three: how would one describe {{char}}’s feeling about the recent progress in life?
---
{% for feeling_memory in feeling_memories -%}
{{loop.index}}. {{feeling_memory}}
{%- endfor %}
---

Return your answers as a numbered list, 1-3, for each of the above corresponding questions.

### Response:
1.\
"""
    )

    @classmethod
    def get_vectordb_queries(cls, char: str, entity: str) -> list[str]:
        q1 = f"How would one describe {char}’s core characteristics?"
        q2 = f"How would one describe {char}’s current daily occupation?"
        q3 = f"How would one describe {char}’s feeling about the recent progress in life?"
        return [q1, q2, q3]

    @classmethod
    def render(
        cls,
        llm: LLM,
        char: str,
        long_description: str,
        characteristic_memories: str,
        occupation_memories: str,
        feeling_memories: str,
        system_prompt: str | None = None,
    ):
        if system_prompt is None:
            system_prompt = llm.default_system_prompt
        return cls.chat_template.render(
            llm=llm,
            system_prompt=system_prompt,
            char=char,
            long_description=long_description,
            characteristic_memories=characteristic_memories,
            occupation_memories=occupation_memories,
            feeling_memories=feeling_memories,
        )

    @classmethod
    def render_instruct(
        cls,
        char: str,
        long_description: str,
        characteristic_memories: str,
        occupation_memories: str,
        feeling_memories: str,
    ):
        return cls.instruct_template.render(
            char=char,
            long_description=long_description,
            characteristic_memories=characteristic_memories,
            occupation_memories=occupation_memories,
            feeling_memories=feeling_memories,
        )
