from pydantic import BaseModel

from clonr.llms import LLM
from clonr.templates.base import Template, env


class SummaryExample(BaseModel):
    passage: str
    summary: str


class OnlineSummaryExample(BaseModel):
    passage: str
    prev_summary: str
    summary: str


DEFAULT_SYSTEM_PROMPT = "You are an imitation AI. You assume the identity of the character you are given, and respond only as that character."


class Message(Template):
    chat_template = env.from_string(
        """\
{{ llm.system_start -}}
{{ system_prompt }}
{{- llm.system_end }}

{{ llm.user_start -}}
The following is a profile describing {{char}}. You are {{char}}. Respond only as {{char}}. Do not break \
character.

Name: {{char}}
{{short_description}}

### Core characteristics:
{{long_description}}

### Example dialogues
{{example_dialogues}}

### Current thoughts and 

TODO

{{- llm.user_end }}

{{ llm.assistant_start -}}
UPDATED DESCRIPTION:
{{ llm.assistant_end -}}
"""
    )

    instruct_template = env.from_string(
        """\
Below is an instruction that describes a task. Write a response that \
appropriately completes the request

### Instruction: 

### Response:
"""
    )

    @classmethod
    def render(
        cls,
        current_description: str,
        document_type: str,
        document_content: str,
        llm: LLM,
        system_prompt: str | None = None,
    ):
        system_prompt = (
            DEFAULT_SYSTEM_PROMPT if system_prompt is None else system_prompt
        )
        return cls.chat_template.render(
            llm=llm,
            current_description=current_description,
            document_type=document_type,
            document_content=document_content,
            system_prompt=system_prompt,
        )

    @classmethod
    def render_instruct(
        cls, current_description: str, document_type: str, document_content: str
    ):
        return cls.instruct_template.render(
            current_description=current_description,
            document_type=document_type,
            document_content=document_content,
        )
