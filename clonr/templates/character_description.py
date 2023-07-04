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


DEFAULT_SYSTEM_PROMPT = "You are a helpful and attentative AI with a deep understanding of human behavior. You give thoughtful, knowledgeable, and well-motivated answers to questions."


class LongDescription(Template):
    chat_template = env.from_string(
        """\
{{ llm.system_start -}}
{{ system_prompt }}
{{- llm.system_end }}

{{ llm.user_start -}}
You are building a character description of an individual. The description should contain \
espouse that individuals core characteristics and includes, but is not limited to, the following:
* personality traits: Innate qualities that shape an individual's behavior and emotional patterns.
* values and beliefs: The principles and convictions that guide a person's decisions and actions.
* experiences: Past events and encounters that shape perspectives, resilience, and personal growth.
* relationships: Connections with family, friends, and social interactions that influence emotional well-being and behavior.
* communication style: The way a person expresses themselves verbally and non-verbally.
* goals and aspirations: The desires and ambitions that drive actions and decision-making.
* moral compass: The sense of right and wrong, ethical standards, and integrity that guide behavior.
* coping mechanisms: How an individual deals with stress, challenges, and setbacks.
* empathy and compassion: The ability to understand and share the feelings of others, and to act with kindness and consideration.
* self-awareness: The ability to reflect on oneself, emotions, and thoughts, and to make conscious choices based on that understanding.

You are constructing this description by iteratively reading a collection \
of documents about the individual. These documents range from self-written notes, to personal websites, \
to snippets of their dialogues. For each excerpt, you update your character description. \
Currently, you have written the following description of this individual (enclosed with ---).

---
DESCRIPTION:
{{ current_description }}
---

Next, you are given the following excerpt (enclosed with ---) taken from a {{ document_type }}.
---
{{ document_type.upper() }}:
{{ document_content }}
---

Given your current character description and the new excerpt, please update your character \
description accordingly. If the new excerpt adds no information, return the original description. \
Your character description should be no longer than 6 paragraphs, be written concisely, fluidly, \
and it should contain as much salient information about the individual as possible.
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
You are building a character description of an individual. The description should contain \
espouse that individuals core characteristics and includes, but is not limited to, the following:
* personality traits: Innate qualities that shape an individual's behavior and emotional patterns.
* values and beliefs: The principles and convictions that guide a person's decisions and actions.
* experiences: Past events and encounters that shape perspectives, resilience, and personal growth.
* relationships: Connections with family, friends, and social interactions that influence emotional well-being and behavior.
* communication style: The way a person expresses themselves verbally and non-verbally. This includes their speech patterns and how they react in conversation.
* goals and aspirations: The desires and ambitions that drive actions and decision-making.
* moral compass: The sense of right and wrong, ethical standards, and integrity that guide behavior.
* coping mechanisms: How an individual deals with stress, challenges, and setbacks.
* empathy and compassion: The ability to understand and share the feelings of others, and to act with kindness and consideration.
* self-awareness: The ability to reflect on oneself, emotions, and thoughts, and to make conscious choices based on that understanding.

You are constructing this description by iteratively reading a collection \
of documents about the individual. These documents range from self-written notes, to personal websites, \
to snippets of their dialogues. For each excerpt, you update your character description. \
Currently, you have written the following description of this individual (enclosed with ---).

---
DESCRIPTION:
{{ current_description }}
---

Next, you are given the following excerpt (enclosed with ---) taken from a {{ document_type }}.
---
{{ document_type.upper() }}:
{{ document_content }}
---

Using only information provided in your current character description, the new excerpt, \
and nothing else, please update your character description accordingly. Do not make up information \
That is not supported by the text. If the new excerpt adds no information, return the original description. \
Your character description should be no longer than 6 paragraphs, be written concisely, fluidly, \
and it should contain as much salient information about the individual as possible.

### Response:
UPDATED DESCRIPTION:
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
