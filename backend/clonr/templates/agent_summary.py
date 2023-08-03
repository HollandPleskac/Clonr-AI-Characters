from clonr.data_structures import Memory
from clonr.llms import LLM
from clonr.templates.base import Template, env

DEFAULT_AGENT_SUMMARY_QUESTIONS = [
    "How would one describe {char}’s core characteristics?",
    "How would one describe {char}’s feeling about their recent progress in life?"
    # 'How would one describe {char}’s current daily occupation?',
]


# TODO: Think if we really want to do numbered outputs. It might be enought to ask to just
# answer all questions, without having to guide it. In any event, we can parse numbere output with
# re.split(r'\n\d\.\s*', string)
class AgentSummary(Template):
    chat_template = env.from_string(
        """\
{{ llm.system_start -}}
{{ system_prompt }}
{{- llm.system_end }}

{{ llm.user_start -}}
You are answering questions about {{char}}.
{% if (short_description) -%}{{short_description}}{%- endif %}
{% if (long_description) -%}
The following (enclosed with ---) are the innate traits and core characteristics of {{char}}. These do not change easily.
---
{{long_description}}
---
{% endif %}
You have gathered the following relevant memories (enclosed with ---) that you will use to answer questions. \
Memories are thoughts, feelings, actions, or observations that {{char}} has had or taken in the past.
---
{% for memory in memories -%}
{{loop.index}}. {{memory}}
{%- if not loop.last %}
{% endif %}
{%- endfor %} 
---
Using only the above information, and not prior knowledge, \
answer the following questions about {{char}}.
{% for question in questions -%}
{{loop.index}}. {{question}}
{%- if not loop.last %}
{% endif %}
{%- endfor %}

Return your answers as a numbered list, \
with the number corresponding to which of the above questions is being answered.
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
You are answering questions about {{char}}.
{% if (short_description) -%}{{short_description}}{%- endif %}
{% if (long_description) -%}
The following (enclosed with ---) are the innate traits and core characteristics of {{char}}. These do not change easily.
---
{{long_description}}
---
{% endif %}
You have gathered the following relevant memories (enclosed with ---) that you will use to answer questions. \
Memories are thoughts, feelings, actions, or observations that {{char}} has had or taken in the past.
---
{% for memory in memories -%}
{{loop.index}}. {{memory}}
{%- if not loop.last %}
{% endif %}
{%- endfor %} 
---

Using only the above information, and not prior knowledge, \
answer the following questions about {{char}}.
{% for question in questions -%}
{{loop.index}}. {{question}}
{%- if not loop.last %}
{% endif %}
{%- endfor %}

Return your answers as a numbered list, \
with the number corresponding to which of the above questions is being answered.

### Response:
1.\
"""
    )

    @classmethod
    def render(
        cls,
        llm: LLM,
        char: str,
        memories: list[str] | list[Memory],
        questions: list[str] | None = None,
        long_description: str | None = None,
        short_description: str | None = None,
        system_prompt: str | None = None,
    ):
        if system_prompt is None:
            system_prompt = llm.default_system_prompt
        if questions is None:
            questions = DEFAULT_AGENT_SUMMARY_QUESTIONS
        try:
            questions = [x.format(char=char) for x in questions]
        except KeyError as e:
            raise KeyError(
                (
                    "When passing custom questions, "
                    "you must format the clone's name as {char}. "
                    f"{e}"
                )
            )
        memories_ = [m if isinstance(m, str) else m.to_str() for m in memories]
        return cls.chat_template.render(
            llm=llm,
            system_prompt=system_prompt,
            char=char,
            long_description=long_description,
            memories=memories_,
            questions=questions,
            short_description=short_description,
        )

    @classmethod
    def render_instruct(
        cls,
        char: str,
        memories: list[str] | list[Memory],
        long_description: str | None = None,
        short_description: str | None = None,
        questions: list[str] | None = None,
    ):
        if questions is None:
            questions = DEFAULT_AGENT_SUMMARY_QUESTIONS
        try:
            questions = [x.format(char=char) for x in questions]
        except KeyError as e:
            raise KeyError(
                (
                    "When passing custom questions, "
                    "you must format the clone's name as {char}. "
                    f"{e}"
                )
            )
        memories = [m if isinstance(m, str) else m.to_str() for m in memories]
        return cls.instruct_template.render(
            char=char,
            long_description=long_description,
            memories=memories,
            questions=questions,
            short_description=short_description,
        )
