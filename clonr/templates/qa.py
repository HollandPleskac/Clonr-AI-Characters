from pydantic import BaseModel

from clonr.llms import LLM
from clonr.templates.base import Template, env


class Excerpt(BaseModel):
    excerpt: str
    summary: str | None = None


QA_EXAMPLE_QUESTION = "What happened one night in October of 2003?"
QA_EXAMPLE_EXCERPT = Excerpt(
    excerpt="""Over the next several years I wrote lots of essays about all kinds of different topics. O'Reilly reprinted a collection of them as a book, called Hackers & Painters after one of the essays in it. I also worked on spam filters, and did some more painting. I used to have dinners for a group of friends every thursday night, which taught me how to cook for groups. And I bought another building in Cambridge, a former candy factory (and later, twas said, porn studio), to use as an office. One night in October 2003 there was a big party at my house. It was a clever idea of my friend Maria Daniels, who was one of the thursday diners. Three separate hosts would all invite their friends to one party. So for every guest, two thirds of the other guests would be people they didn't know but would probably like. One of the guests was someone I didn't know but would turn out to like a lot: a woman called Jessica Livingston. A couple days later I asked her out. Jessica was in charge of marketing at a Boston investment bank.""",
    summary="""The passage describes the author's experiences writing essays, working on spam filters, and hosting dinners for friends. The author meets a woman named Jessica Livingston and they decide to start their own investment firm. They create Y Combinator (YC), which focuses on funding startups and providing support and guidance. YC adopts a batch model, funding multiple startups at once and offering a three-month program to help them. The author realizes the benefits of scaling startup funding and the advantages of having a community of alumni. YC becomes a significant part of the author's life, taking up more of their attention.""",
)
# Note, the expected answer using LlamaCpp for the above examples should be
"""In October 2003, Paul Graham had a big party at his house, where he
met Jessica Livingston for the first time. Later that month, they
started Y Combinator together. YC has since funded hundreds of
startups and grown to become a worldwide community of entrepreneurs."""
# which is spot on. But it's fucking weird since the data never mentions Paul Graham
# by name... fuck.


class QuestionAndAnswer(Template):
    _system_prompt = """You are a helpful AI assistant with access to a large database of documents used for answering questions. You answer questions truthfully and accurately."""

    chat_template = env.from_string(
        """\
{{ llm.system_start -}}
{{ system_prompt }}
{{- llm.system_end }}

{{ llm.user_start -}}
Answer the following question.
QUESTION: {{ question }}

Begin your answer with "ANSWER:".
{{- llm.user_end }}

{{ llm.assistant_start -}}
{% if (excerpts) -%}
I have retrieved the following excerpts of documents from my database that may be helpful in answering you question.
{% for e in excerpts -%}
--- Excerpt {{ loop.index }} ---
{{e.excerpt}}
---
{% if (e.summary) -%}
To better understand the above excerpt, I have summarized the document it came from below.
--- Summary {{ loop.index }} ---
{{ e.summary }}
---
{%- endif %}
{%- endfor %}
{%- endif %}
Based only on the information above, and not prior knowledge, here is my answer.
ANSWER:\
{{- llm.assistant_end -}}
"""
    )

    instruct_template = env.from_string(
        """\
Below is an instruction that describes a task. Write a response that \
appropriately completes the request

### Instruction: 
{{ system_prompt }}

Answer the following question.
QUESTION: {{ question }}

Begin your answer with "ANSWER:".

### Response:
{% if (excerpts) -%}
I have retrieved the following excerpts of documents from my database that may be helpful in answering you question.
{% for e in excerpts -%}
--- Excerpt {{ loop.index }} ---
{{e.excerpt}}
---
{% if (e.summary) -%}
To better understand the above excerpt, I have summarized the document it came from below.
--- Summary {{ loop.index }} ---
{{ e.summary }}
---
{%- endif %}
{%- endfor %}
{%- endif %}
Based only on the information above, and not prior knowledge, here is my answer.
ANSWER:\
"""
    )

    @classmethod
    def render(
        cls,
        question: str,
        llm: LLM,
        excerpts: list[Excerpt] | None = None,
        system_prompt: str | None = None,
    ):
        system_prompt = cls._system_prompt if system_prompt is None else system_prompt
        if not excerpts:
            excerpts = None
        return cls.chat_template.render(
            llm=llm, question=question, excerpts=excerpts, system_prompt=system_prompt
        )

    @classmethod
    def render_instruct(cls, question: str, excerpts: list[Excerpt] | None = None):
        return cls.instruct_template.render(
            question=question, excerpts=excerpts, system_prompt=cls._system_prompt
        )
