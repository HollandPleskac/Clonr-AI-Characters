from clonr.data_structures import Dialogue, Memory
from clonr.data_structures import Message as MessageStruct
from clonr.llms import LLM
from clonr.templates.base import Template, env
from clonr.utils import get_current_datetime
from clonr.utils.formatting import DateFormat

DEFAULT_SYSTEM_PROMPT = "You are an imitation AI. You assume the identity of the character you are given, and respond only as that character."


def cur_time():
    return DateFormat.human_readable(
        get_current_datetime(), use_today_and_yesterday=False
    )


class Message(Template):
    chat_template = env.from_string(
        """\
{{ llm.system_start -}}
{{ system_prompt }}
{{- llm.system_end }}

{{ llm.user_start -}}
You are {{char}}. Each section of your profile will be enclosed with ---. The following \
are your innate characteristics and fundamental qualities. These do not change easily.
---
Name: {{char}}
{{short_description}}

### Core characteristics
{{long_description}}
\
{%- if (example_dialogues) -%}
### Example dialogues
{{example_dialogues}}
{%- endif %}
\
---

The following describes your current state. It contains a summary of your current state \
and a list of retrieved memories. \
Memories are thoughts, observations, actions, or reflections that you've had.
---
{% if (agent_summary) -%}
{{agent_summary}}
{%- endif %}
### Retrieved memories
{% for memory in memories -%}
{{memory}}
{%- endfor %}
---

These are your thoughts and feelings about {{entity_name}}.
---
{{entity_context_summary}}
---

Finally, the following are your most recent messages of your conversation with {{entity_name}}.
---
{% for msg in messages -%}
{{msg}}
{%- endfor %}
---

The current datetime is {{cur_time}}}. \
You are {{char}}. Respond to these messages as {{char}}. \
Respond only as {{char}} and do not break character. \
Separate distinct messages by using a newline.
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
You are an imitation AI. You assume the identity of the character you are given, \
and respond only as that character. Each section of your profile will be enclosed \
with ---. The following are your innate characteristics and fundamental qualities. \
These do not change easily.
---
Name: {{char}}
{{short_description}}

### Core characteristics
{{long_description}}

### Example dialogues
{% for dialogue in example_dialogues -%}
Dialogue #{{ loop.index }}:
{% for msg in dialogue -%}
{% if (msg.is_character) -%}{{char}}{%- else -%}{{ msg.speaker }}{%- endif %}: {{ msg.content }}
{%- endfor %}
{%- endfor %}
---

The following describes your current state. It contains a summary of your current state \
and a list of retrieved memories. \
Memories are thoughts, observations, actions, or reflections that you've had.
---
{% if (agent_summary) -%}
{{agent_summary}}
{%- endif %}
### Retrieved memories
{% for memory in memories -%}
{{memory}}
{%- endfor %}
---

These are your thoughts and feelings about {{entity_name}}.
---
{{entity_context_summary}}
---

Finally, the following are your most recent messages of your conversation with {{entity_name}}.
---
{% for msg in messages -%}
{{msg}}
{%- endfor %}
---

You are {{char}} and you should respond to these messages as {{char}}. \
Respond only as {{char}} and do not break character. \
Separate distinct messages by using a newline.

### Response:
"""
    )

    @classmethod
    def render(
        cls,
        char: str,
        short_description: str,
        long_description: str,
        example_dialogues: list[Dialogue],
        agent_summary: str,
        memories: list[str] | list[Memory],
        entity_context_summary: str,
        entity_name: str,
        messages: list[str] | list[MessageStruct],
        llm: LLM,
        system_prompt: str | None = None,
    ):
        system_prompt = (
            DEFAULT_SYSTEM_PROMPT if system_prompt is None else system_prompt
        )

        memories = [m if isinstance(m, str) else m.to_str() for m in memories]
        messages = [m if isinstance(m, str) else m.to_str() for m in messages]
        return cls.chat_template.render(
            char=char,
            short_description=short_description,
            long_description=long_description,
            example_dialogues=example_dialogues,
            agent_summary=agent_summary,
            memories=memories,
            entity_context_summary=entity_context_summary,
            messages=messages,
            llm=llm,
            entity_name=entity_name,
            cur_time=cur_time(),
            system_prompt=system_prompt,
        )

    @classmethod
    def render_instruct(
        cls,
        char: str,
        short_description: str,
        long_description: str,
        example_dialogues: list[Dialogue],
        agent_summary: str,
        memories: list[str] | list[Memory],
        entity_context_summary: str,
        entity_name: str,
        messages: list[str] | list[MessageStruct],
    ):
        memories = [m if isinstance(m, str) else m.to_str() for m in memories]
        messages = [m if isinstance(m, str) else m.to_str() for m in messages]
        return cls.instruct_template.render(
            char=char,
            short_description=short_description,
            long_description=long_description,
            example_dialogues=example_dialogues,
            agent_summary=agent_summary,
            memories=memories,
            entity_name=entity_name,
            cur_time=cur_time(),
            entity_context_summary=entity_context_summary,
            messages=messages,
        )
