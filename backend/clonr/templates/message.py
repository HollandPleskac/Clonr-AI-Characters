import re

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


# TODO (Jonny): we are missing the fact retrieval here!!
class Message(Template):
    chat_template = env.from_string(
        """\
{{ llm.system_start -}}
{{ system_prompt }}
{{- llm.system_end }}

{{ llm.user_start -}}
You are {{char}}. Each section of your profile will begin with ###. The following \
are your innate characteristics and fundamental qualities. These do not change easily.

### Core characteristics
{{short_description}}

{{long_description}}

{%- if (example_dialogues) %}
### Example dialogues
{{example_dialogues}}
{%- endif %}

{% if (agent_summary) -%}
### Current state
The following describes your current state of mind.
{%- endif %}

### Retrieved memories
The following is a list of retrieved memories useful for deducing your current state. \
Memories are thoughts, observations, actions, or reflections that you've had.
{% for memory in memories -%}
{{memory}}
{%- endfor %}

{% if (entity_context_summary) -%}
### Relationship to {{entity_name}}
These are your thoughts and feelings about {{entity_name}}.
{{entity_context_summary}}
{%- endif %}

### Current conversation
Finally, the following are your most recent messages of your conversation with {{entity_name}}.
{% for msg in messages -%}
{{msg}}
{%- endfor %}

The current time is {{cur_time}}. \
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
You are {{char}}. Each section of your profile will begin with ###. The following \
are your innate characteristics and fundamental qualities. These do not change easily.

### Core characteristics
{{short_description}}
{{long_description}}
{% if (example_dialogues) %}
### Example dialogues
{% for dialogue in example_dialogues -%}
{{dialogue}}
{% if not loop.last %}
{% endif %}
{%- endfor %}
{%- endif %}
{% if (agent_summary) -%}
### Current state
The following describes your current state of mind.
{%- endif %}
### Retrieved memories
The following is a list of useful memories that you've recalled. \
Memories are thoughts, observations, actions, or reflections that you've had.
{% for memory in memories -%}
{{memory}}
{%- if not loop.last %}
{% endif %}
{%- endfor %}
{% if (entity_context_summary) %}
### Relationship to {{entity_name}}
The following are your thoughts and feelings about {{entity_name}}.
{{entity_context_summary}}
{%- endif %}

### Current conversation
Finally, the following are your most recent messages of your conversation with {{entity_name}}.
{% for msg in messages -%}
{{msg}}
{%- if not loop.last %}
{% endif %}
{%- endfor %}

The current datetime is {{cur_time}}. \
You are {{char}}. Respond to the last message by {{entity_name}}.
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

        # TODO (Jonny): we need to prevent overlap here, where the retrieved memories
        # are equivalent to the past messages. not sure if that should be taken care
        # of at the DB level or as post filtering here.
        memories = [m if isinstance(m, str) else m.to_str() for m in memories]
        messages = [m if isinstance(m, str) else m.to_str() for m in messages]
        dialogues = [x.to_str() for x in example_dialogues]
        return cls.chat_template.render(
            char=char,
            short_description=short_description,
            long_description=long_description,
            example_dialogues=dialogues,
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
        dialogues = [x.to_str() for x in example_dialogues]
        return cls.instruct_template.render(
            char=char,
            short_description=short_description,
            long_description=long_description,
            example_dialogues=dialogues,
            agent_summary=agent_summary,
            memories=memories,
            entity_name=entity_name,
            cur_time=cur_time(),
            entity_context_summary=entity_context_summary,
            messages=messages,
        )


class MessageQuery(Template):
    chat_template = env.from_string(
        """\
{{ llm.system_start -}}
{{ system_prompt }}
{{- llm.system_end }}

{{ llm.user_start -}}
The current time is {{cur_time}}. \
You are analyzing a conversation between yourself ({{char}}) and {{entity_name}}.\
{%- if (short_description) %} You ({{char}}) are described as follows.
---
{{short_description}}
{% if (agent_summary) -%}
{{agent_summary}}
{%- endif %}
---
{%- endif %}
{% if (entity_context_summary) -%}
{{char}}'s relationship to {{entity_name}} can be described as follows.
---
{{entity_context_summary}}
---
{%- endif %}
Read the following conversation (enclosed with ---) bewteen {{char}} and {{entity_name}} (enclosed with ---) and answer the question that follows.
---
{% for msg in messages -%}
{{msg}}
{%- if not loop.last %}
{% endif %}
{%- endfor %}
---
In order to write a response to {{entity_name}}, what questions do you need answered? \
Write at most 3 questions. Format your response as JSON list. Refer to youself in first person. \
If you have no questions, simply return the last message in the conversation.
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
You are analyzing a conversation between yourself ({{char}}) and {{entity_name}}.

{% if (short_description) -%}
You ({{char}}) are described as follows.
{{short_description}}
{% if (agent_summary) %}{{agent_summary}}{% endif %}
{%- endif %}

{% if (entity_context_summary) -%}
Your relationship with {{entity_name}} can be described as follows.
{{entity_context_summary}}
{%- endif %}

Read the following conversation bewteen you and {{entity_name}}, \
and answer the question that follows. The current time is {{cur_time}}.
{% for msg in messages -%}
{{msg}}
{%- if not loop.last %}
{% endif %}
{%- endfor %}

In order to write a response to {{entity_name}}, what questions should you ask yourself? \
Write at most 3 questions. Format your response as JSON list. Refer to youself in first person. \
If you have no questions, simply return the last message in the conversation.

### Response:
["\
"""
    )

    @classmethod
    def render(
        cls,
        char: str,
        short_description: str,
        agent_summary: str,
        entity_context_summary: str,
        entity_name: str,
        messages: list[str] | list[MessageStruct],
        llm: LLM,
        system_prompt: str | None = None,
    ):
        system_prompt = (
            DEFAULT_SYSTEM_PROMPT if system_prompt is None else system_prompt
        )

        messages = [m if isinstance(m, str) else m.to_str() for m in messages]
        s = cls.chat_template.render(
            char=char,
            short_description=short_description,
            agent_summary=agent_summary,
            entity_context_summary=entity_context_summary,
            messages=messages,
            llm=llm,
            entity_name=entity_name,
            cur_time=cur_time(),
            system_prompt=system_prompt,
        )
        return re.sub(r"\n\n+", "\n", s)

    @classmethod
    def render_instruct(
        cls,
        char: str,
        short_description: str,
        agent_summary: str,
        entity_context_summary: str,
        entity_name: str,
        messages: list[str] | list[MessageStruct],
    ):
        messages = [m if isinstance(m, str) else m.to_str() for m in messages]
        s = cls.instruct_template.render(
            char=char,
            short_description=short_description,
            agent_summary=agent_summary,
            entity_name=entity_name,
            cur_time=cur_time(),
            entity_context_summary=entity_context_summary,
            messages=messages,
        )
        # The whitespace was fucking killing me here (Jonny)
        # I spent like 40 minutes on this and couldn't get it to work.
        return re.sub(r"\n\n+", "\n\n", s)
