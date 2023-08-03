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


DEFAULT_SUMMARIZE_EXAMPLE = SummaryExample(
    passage="""On the surface, Makima seems to be a nice, gentle, social and friendly woman who is almost seen wearing a smile on her face the entire time and acts relaxed and confident even during a crisis, speaking in a professional tone to her workers. As her natural appearance is nearly identical to that of a human, she avoids disclosing her Devil nature to most of her underlings and spends much of the series posing as a human contracted to a Devil rather than a Devil herself. However, this is only a façade that she uses to fulfill her ultimate goal: After the death of Aki Hayakawa, Makima begins to reveal her true colors to Denji. Makima's true face is of someone that is Machiavellian and calculating, who sees people around her as nothing more than "dogs" she can use as she much as she likes and must obey her without any hesitation.""",
    summary='Makima is a calm, collected devil with the appearance of a human, who puts on an outwardly kind and friendly façade in order to fulfill her ultimate Machiavellian goals. Her core beliefs begin to present themselves to Denji after Aki Hayakawa dies. She believes those around her are her "dogs", that should obey her without hesitation.',
)

DEFAULT_ONLINE_SUMMARIZE_EXAMPLE = OnlineSummaryExample(
    prev_summary="Harry was a poor, orphaned boy. Both of his parents vanished at a young age, leaving Harry in the custody of his aunt and uncle. His life changed when he met Hagrid, a gentle, kind wizard who informed harry that, he too, was a wizard.",
    passage="Harry later came to find that Hagrid was not a kind, nor gentle wizard at all. In fact, he was quite the opposite, a cunning and calculating wizard, intent only on furthering his own objectives. Harry would come to find that it was in fact Hagrid, who murdered his parents.",
    summary="Harry was a poor, orphaned boy. Both of his parents vanished at a young age, leaving Harry in the custody of his aunt and uncle. His life changed when he met Hagrid, a wizard who informed harry that he too was a wizard. Hagrid seemed kind and gentle, but was not. Harry would later learn that Hagrid killed his parents.",
)


class Summarize(Template):
    """We get a 5 microsecond latency hit for using jinja.
    An f-string would just be 1 microsecond"""

    chat_template = env.from_string(
        """\
{{ llm.system_start -}}
{{ system_prompt }}
{{- llm.system_end }}

{{ llm.user_start -}}
Summarize the following passage (enclosed with ---), using only the \
text in the passage and not prior knowledge. \
Write a brief and straightforward summarization, that includes as many \
key points and as much salient information as possible. \
Use only information present in the passage.
---
{{passage}}
---
{{- llm.user_end }}

{{ llm.assistant_start -}}
Summary:
{{- llm.assistant_end -}}
"""
    )

    instruct_template = env.from_string(
        """\
Below is an instruction that describes a task. Write a response that \
appropriately completes the request

### Instruction:
Summarize the following passage (enclosed with ---), using only the \
text in the passage and not prior knowledge. \
Write a brief and straightforward summarization, that includes as many \
key points and as much salient information as possible. \
Use only information present in the passage.
---
{{passage}}
---

### Response:
Summary:\
"""
    )

    @classmethod
    def render(cls, passage: str, llm: LLM, system_prompt: str | None = None):
        system_prompt = (
            llm.default_system_prompt if system_prompt is None else system_prompt
        )
        return cls.chat_template.render(
            llm=llm, passage=passage, system_prompt=system_prompt
        )

    @classmethod
    def render_instruct(cls, passage: str):
        return cls.instruct_template.render(passage=passage)


class SummarizeWithExamples(Template):
    chat_template = env.from_string(
        """\
{{ llm.system_start -}}
{{ system_prompt }}
{{- llm.system_end }}

{{ llm.user_start -}}
Summarize the following passage enclosed with ---, using only the \
text in the passage and not prior knowledge. Write a brief \
and straightforward summarization, that includes as many key points and \
as much salient information as possible. \
Use only information present in the passage. \
Let's try a few examples.
{{- llm.user_end }}

{% for example in examples -%}
{{ llm.user_start -}}
Example #{{ loop.index }}:
---
{{ example.passage }}
---
{{- llm.user_end }}

{{ llm.assistant_start -}}
Summary: {{ example.summary }}
{{- llm.assistant_end }}
{%- endfor %}

{{ llm.user_start -}}
Now summarize the following passage.
---
{{ passage }}
---
{{- llm.user_end }}

{{ llm.assistant_start -}}
Summary:\
{{- llm.assistant_end -}}
"""
    )

    instruct_template = env.from_string(
        """\
Below is an instruction that describes a task. Write a response that \
appropriately completes the request

### Instruction: 
Summarize the following passage (enclosed with ---). using only the \
text in the passage and not prior knowledge. \
Write a brief and straightforward summarization, that includes as many \
key points and as much salient information as possible. \
Use only information present in the passage.

Let's try a few examples.
{% for example in examples -%}
Example #{{ loop.index }}:
---
{{ example.passage }}
---
Summary: {{ example.summary }}
{%- endfor %}

Now summarize the following passage.
---
{{passage}}
---

### Response:
Summary:\
"""
    )

    @classmethod
    def render(
        cls,
        passage: str,
        llm: LLM,
        examples: list[SummaryExample] | None = None,
        system_prompt: str | None = None,
    ):
        system_prompt = (
            llm.default_system_prompt if system_prompt is None else system_prompt
        )
        examples = examples or [DEFAULT_SUMMARIZE_EXAMPLE]
        return cls.chat_template.render(
            llm=llm, passage=passage, system_prompt=system_prompt, examples=examples
        )

    @classmethod
    def render_instruct(
        cls, passage: str, examples: list[SummaryExample] | None = None
    ):
        examples = examples or [DEFAULT_SUMMARIZE_EXAMPLE]
        return cls.instruct_template.render(passage=passage, examples=examples)


class OnlineSummarize(Template):
    chat_template = env.from_string(
        """\
{{ llm.system_start -}}
{{ system_prompt }}
{{- llm.system_end }}

{{ llm.user_start -}}
You are summarizing a long document by reading it from the start and \
updating your summary after every passage that you read. Given the current \
summary along with a new passage, update your summary appropriately. Your summary \
should includes as many key points and as much salient information as possible. \
If the passage introduces important new information, add it to the summary. If the \
passage contains information that should alter the summary, do so appropriately. \
Your updated summarization should remain brief and straightforward.

The current summary (enclosed with ---) is:
---
{{prev_summary}}
---
The new passage (enclosed with ---) is:
---
{{passage}}
---
{{- llm.user_end }}

{{ llm.assistant_start -}}
Summary:\
{{- llm.assistant_end -}}
"""
    )

    instruct_template = env.from_string(
        """\
Below is an instruction that describes a task. Write a response that \
appropriately completes the request

### Instruction: 
You are summarizing a long document by reading it from the start and \
updating your summary after every passage that you read. Given the current \
summary along with a new passage, update your summary appropriately. Your summary \
should includes as many key points and as much salient information as possible. \
If the passage introduces important new information, add it to the summary. If the \
passage contains information that should alter the summary, do so appropriately. \
Your updated summarization should remain brief and straightforward. The current \
summary (enclosed with ---) is:
---
{{prev_summary}}
---
The new passage (enclosed with ---) is:
---
{{passage}}
---

### Response:
Summary:\
"""
    )

    @classmethod
    def render(
        cls, passage: str, prev_summary: str, llm: LLM, system_prompt: str | None = None
    ):
        system_prompt = (
            llm.default_system_prompt if system_prompt is None else system_prompt
        )
        return cls.chat_template.render(
            llm=llm,
            passage=passage,
            system_prompt=system_prompt,
            prev_summary=prev_summary,
        )

    @classmethod
    def render_instruct(cls, passage: str, prev_summary: str):
        return cls.instruct_template.render(passage=passage, prev_summary=prev_summary)


class OnlineSummarizeWithExamples(Template):
    chat_template = env.from_string(
        """\
{{ llm.system_start -}}
{{ system_prompt }}
{{- llm.system_end }}

{{ llm.user_start -}}
You are summarizing a long document by reading it from the start and \
updating your summary after every passage that you read. Given the current \
summary along with a new passage, update your summary appropriately. Your summary \
should includes as many key points and as much salient information as possible. \
If the passage introduces important new information, add it to the summary. If the \
passage contains information that should alter the summary, do so appropriately. \
Your updated summarization should remain brief and straightforward. Let's try some examples.
{{- llm.user_end }}

{% for example in examples -%}
{{ llm.user_start -}}
Example #{{ loop.index }}:
Current summary:
---
{{example.prev_summary}}
---
Passage:
---
{{example.passage}}
---
{{- llm.user_end }}

{{ llm.assistant_start -}}
Summary: {{example.summary}}
{{- llm.assistant_end -}}
{%- endfor %}

{{ llm.user_start -}}
Now complete the task.
Current summary:
---
{{example.prev_summary}}
---
Passage:
---
{{example.passage}}
---
{{- llm.user_end }}

{{ llm.assistant_start -}}
Summary:\
{{- llm.assistant_end -}}
"""
    )

    instruct_template = env.from_string(
        """\
Below is an instruction that describes a task. Write a response that \
appropriately completes the request

### Instruction: 
You are summarizing a long document by reading it from the start and \
updating your summary after every passage that you read. Given the current \
summary along with a new passage, update your summary appropriately. Your summary \
should includes as many key points and as much salient information as possible. \
If the passage introduces important new information, add it to the summary. If the \
passage contains information that should alter the summary, do so appropriately. \
Your updated summarization should remain brief and straightforward. Let's try some examples.

{% for example in examples -%}
Example #{{ loop.index }}:
Current summary:
---
{{example.prev_summary}}
---
Passage:
---
{{example.passage}}
---
Summary: {{example.summary}}
{%- endfor %}

Now complete the task.
Current summary:
---
{{prev_summary}}
---
Passage:
---
{{passage}}
---

### Response:
Summary:\
"""
    )

    @classmethod
    def render(
        cls,
        passage: str,
        prev_summary: str,
        llm: LLM,
        system_prompt: str | None = None,
        examples: list[OnlineSummaryExample] | None = None,
    ):
        system_prompt = (
            llm.default_system_prompt if system_prompt is None else system_prompt
        )
        examples = examples or [DEFAULT_ONLINE_SUMMARIZE_EXAMPLE]
        return cls.chat_template.render(
            llm=llm,
            passage=passage,
            system_prompt=system_prompt,
            prev_summary=prev_summary,
            examples=examples,
        )

    @classmethod
    def render_instruct(
        cls,
        passage: str,
        prev_summary: str,
        examples: list[OnlineSummaryExample] | None = None,
    ):
        examples = examples or [DEFAULT_ONLINE_SUMMARIZE_EXAMPLE]
        return cls.instruct_template.render(
            passage=passage, prev_summary=prev_summary, examples=examples
        )


class SummarizeWithContext(Template):
    chat_template = env.from_string(
        """\
{{ llm.system_start -}}
{{ system_prompt }}
{{- llm.system_end }}

{{ llm.user_start -}}
Given both an excerpt from a long document, and a summary of that document \
up until the excerpt, write a brief and straightforward summarization. Include \
as many key points and as much salient information as possible. \
Summarize only information present in the excerpt, but make use of the previous \
summary where necessary. The current summary (enclosed with ---) is:
---
{{prev_summary}}
---
The excerpt to summarize (enclosed with ---) is:
---
{{passage}}
---
{{- llm.user_end }}

{{ llm.assistant_start -}}
Summary:\
{{- llm.assistant_end -}}
"""
    )

    instruct_template = env.from_string(
        """\
Below is an instruction that describes a task. Write a response that \
appropriately completes the request

### Instruction: 
Given both an excerpt from a long document, and a summary of that document \
up until the excerpt, write a brief and straightforward summarization. Include \
as many key points and as much salient information as possible. \
Summarize only information present in the excerpt, but make use of the previous \
summary where necessary. The current summary (enclosed with ---) is:
---
{{prev_summary}}
---
The excerpt to summarize (enclosed with ---) is:
---
{{passage}}
---

### Response:
Summary:\
"""
    )

    @classmethod
    def render(
        cls, passage: str, prev_summary: str, llm: LLM, system_prompt: str | None = None
    ):
        system_prompt = (
            llm.default_system_prompt if system_prompt is None else system_prompt
        )
        return cls.chat_template.render(
            llm=llm,
            passage=passage,
            system_prompt=system_prompt,
            prev_summary=prev_summary,
        )

    @classmethod
    def render_instruct(cls, passage: str, prev_summary: str):
        return cls.instruct_template.render(passage=passage, prev_summary=prev_summary)
