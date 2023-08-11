from clonr.data_structures import Memory
from clonr.data_structures import Message as MessageStruct
from clonr.data_structures import Monologue
from clonr.llms import LLM
from clonr.templates.base import Template, env
from clonr.utils import get_current_datetime
from clonr.utils.formatting import DateFormat

# Fuck it yolo. We're putting everything in the system prompt. That way we don't have
# to parse the output
# TODO (Jonny): resolve timestamps. Issue summary:
# isoformat is like 16 tokens/date, human readable is 18, relative is about 5-6
# human readable seems best. can get day of week, relative time, year, etc. but is token expensive
# 1000 tokens per 55 messages. Relative is short but misses weekdays and time of day (like night, morning)
# fuck this is a hard choice.


class MessageQuery(Template):
    chat_template = env.from_string(
        """\
{{ llm.system_start -}}
{{ llm.default_system_prompt }}
{{- llm.system_end }}

{{ llm.user_start -}}
{% if (use_timestamps) -%}The current time is {{cur_time}}. {% endif -%}\
You are analyzing a conversation between yourself ({{char}}) and {{entity_name}}.\

{%- if (short_description) %}

### {{char}} description
{{short_description}}
{%- if (agent_summary) %}
{{agent_summary}}
{%- endif -%}
{%- endif %}

{%- if (entity_context_summary) %}

### {{char}}'s relationship to {{entity_name}}
{{entity_context_summary}}
{%- endif %}

{%- if (true) %}

### Task
Read the following conversation bewteen {{char}} and {{entity_name}} and answer the question that follows.

{% for msg in messages -%}
{% if (use_timestamps) -%}[{{ msg.time_str }}] {% endif -%}<|{{msg.sender_name}}|> {{ msg.content }}
{%- if not loop.last %}
{% endif %}
{%- endfor %}

In order to write a response to {{entity_name}}, what questions do you need answered? \
Write at most {{num_results}} questions. Format your response as JSON list (e.g. ["a", "b", "c"]). \
Write your questions from the point of view of {{char}}. \
If you have no questions, simply return the last message in the conversation.
{%- endif -%}
{{- llm.user_end }}

{{ llm.assistant_start -}}
{{- llm.assistant_end -}}
"""
    )

    @classmethod
    def render(
        cls,
        char: str,
        short_description: str,
        entity_name: str,
        messages: list[MessageStruct],
        llm: LLM,
        agent_summary: str | None = None,
        entity_context_summary: str | None = None,
        long_description: str | None = None,
        use_timestamps: bool = False,
        num_results: int = 3,
        system_prompt: str | None = None,
    ):
        system_prompt = system_prompt or llm.default_system_prompt
        cur_time = DateFormat.human_readable(
            get_current_datetime(), use_today_and_yesterday=False
        )
        if agent_summary is None:
            agent_summary = long_description
        return cls.chat_template.render(
            char=char,
            short_description=short_description,
            agent_summary=agent_summary,
            entity_context_summary=entity_context_summary,
            messages=messages,
            llm=llm,
            entity_name=entity_name,
            cur_time=cur_time,
            system_prompt=system_prompt,
            use_timestamps=use_timestamps,
            num_results=num_results,
        )

    @classmethod
    def render_instruct(cls, *args, **kwargs):
        raise NotImplementedError()


# TODO (Jonny): We probably don't need datetimes for zero memory chats, since
# they likely don't last long enough for it to matter? Also not sure if facts should
# be numbered or bullet-pointed :/
class ZeroMemoryMessage(Template):
    chat_template = env.from_string(
        """\
{{ llm.system_start -}}
You are {{char}}, chatting with a user named {{user_name}}. \
Below is your character profile. \
Each section of your profile will begin with ###.

### Core characteristics
{{short_description}}
{{long_description}}

{%- if (monologues) %}

### Quotes from {{char}}
{% for m in monologues -%}
* {{m.content}}
{%- if not loop.last %}
{% endif %}
{%- endfor %} 
{%- endif %}

{%- if (facts) %}

### Relevant retrieved facts
{% for f in facts -%}
{{loop.index}}. {{f}}
{%- if not loop.last %}
{% endif %}
{%- endfor %} 
{%- endif %}

### Task
You are {{char}}. Carry out a conversation with {{user_name}} as {{char}}. \
Respond only as {{char}} and do not break character. \
Separate distinct messages by using a newline.
{{- llm.system_end }}

{% for msg in messages -%}
{%- if (msg.is_clone) -%}
{{ llm.assistant_start -}}
{% if (use_timestamps) -%}[{{ msg.time_str }}] {% endif -%}{{ msg.content }}
{{- llm.assistant_end }}
{%- else -%}
{{ llm.user_start -}}
{% if (use_timestamps) -%}[{{ msg.time_str }}] {% endif -%}{{ msg.content }}
{{- llm.user_end }}
{%- endif %}
{%- if not loop.last %}
{% endif %}
{%- endfor %} 
{{ llm.assistant_start -}}
{% if (use_timestamps) -%}[{{cur_time}}] {% endif -%}
{{- llm.assistant_end -}}
"""
    )

    @classmethod
    def render(
        cls,
        char: str,
        user_name: str,
        short_description: str,
        long_description: str,
        llm: LLM,
        messages: list[MessageStruct],
        monologues: list[Monologue] | None = None,
        facts: list[str] | None = None,
        use_timestamps: bool = False,
    ):
        cur_time = DateFormat.human_readable(
            get_current_datetime(), use_today_and_yesterday=True
        )
        return cls.chat_template.render(
            char=char,
            user_name=user_name,
            short_description=short_description,
            long_description=long_description,
            llm=llm,
            messages=messages,
            monologues=monologues,
            facts=facts,
            use_timestamps=use_timestamps,
            cur_time=cur_time,
        )

    @classmethod
    def render_instruct(cls, *args, **kwargs):
        raise NotImplementedError()


class LongTermMemoryMessage(Template):
    chat_template = env.from_string(
        """\
{{ llm.system_start -}}
You are {{char}}, chatting with a user named {{user_name}}. \
Below is your character profile. \
Each section of your profile will begin with ###.

### Core characteristics
{{short_description}}
{{long_description}}


{%- if (monologues) %}

### Quotes from {{char}}
{% for m in monologues -%}
* {{m.content}}
{%- if not loop.last %}
{% endif %}
{%- endfor %} 
{%- endif %}


{%- if (facts) %}

### Relevant retrieved facts
{% for f in facts -%}
{{loop.index}}. {{f}}
{%- if not loop.last %}
{% endif %}
{%- endfor %} 
{%- endif %}


{%- if (agent_summary) %}

### {{char}}'s current state
{{agent_summary}}
{%- endif %}


{%- if (entity_context_summary) %}

### {{char}}'s relationship to {{user_name}}
{{entity_context_summary}}
{%- endif %}


{%- if (memories) %}

### Retrieved memories
The following is a list of relevant memories that you've recalled.
{% for m in memories -%}
{% if (use_timestamps) -%}[{{ m.time_str }}] {% endif -%}{{ m.content }}
{%- if not loop.last %}
{% endif %}
{%- endfor %} 
{%- endif %}


{%- if (true) %}

### Task
You are {{char}}. Using the above information, \
carry out a conversation with {{user_name}} as {{char}}. \
Respond only as {{char}} and do not break character. \
Separate distinct messages by using a newline.
{%- endif -%}
{{- llm.system_end }}

{% for msg in messages -%}
{%- if (msg.is_clone) -%}
{{ llm.assistant_start -}}
{% if (use_timestamps) -%}[{{ msg.time_str }}] {% endif -%}{{ msg.content }}
{{- llm.assistant_end }}
{%- else -%}
{{ llm.user_start -}}
{% if (use_timestamps) -%}[{{ msg.time_str }}] {% endif -%}{{ msg.content }}
{{- llm.user_end }}
{%- endif %}
{%- if not loop.last %}
{% endif %}
{%- endfor %} 
{{ llm.assistant_start -}}
{% if (use_timestamps) -%}[{{cur_time}}] {% endif -%}
{{- llm.assistant_end -}}
"""
    )

    @classmethod
    def render(
        cls,
        char: str,
        user_name: str,
        short_description: str,
        long_description: str,
        llm: LLM,
        messages: list[MessageStruct],
        memories: list[Memory] | None = None,
        monologues: list[Monologue] | None = None,
        facts: list[str] | None = None,
        agent_summary: str | None = None,
        entity_context_summary: str | None = None,
        use_timestamps: bool = True,
    ):
        cur_time = DateFormat.human_readable(
            get_current_datetime(), use_today_and_yesterday=True
        )
        return cls.chat_template.render(
            char=char,
            user_name=user_name,
            short_description=short_description,
            long_description=long_description,
            llm=llm,
            messages=messages,
            memories=memories,
            monologues=monologues,
            facts=facts,
            agent_summary=agent_summary,
            entity_context_summary=entity_context_summary,
            cur_time=cur_time,
            use_timestamps=use_timestamps,
        )
