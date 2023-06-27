# import guidance
from pydantic import BaseModel

from clonr.llms import LLM
from clonr.templates.base import env, Template


class Summary(BaseModel):
    passage: str
    summary: str

    def render_task(self, header: str = ""):
        return f"{header}Passage: {self.passage}\nSummary:"

    def render(self, header: str = ""):
        return f"{self.render_task(header=header)} {self.summary}"

    def render_task_as_chat(self, llm: LLM, header: str = ""):
        return f"{llm.user_start}{header}Passage: {self.passage}{llm.user_end}\n\n{llm.assistant_start}Summary:"

    def render_as_chat(self, llm: LLM, header: str = ""):
        return f"{self.render_task_as_chat(llm=llm, header=header)} {self.summary}{llm.assistant_end}"


class SummaryWithContext(Summary):
    context: str

    def render_task(self, header: str = ""):
        return f"{header}Context: {self.context}\nPassage: {self.passage}\nSummary:"

    def render(self, header: str = ""):
        return f"{self.render_task(header=header)} {self.summary}"

    def render_task_as_chat(self, llm: LLM, header: str = ""):
        return f"{llm.user_start}{header}Context: {self.context}\nPassage: {self.passage}{llm.user_end}\n\n{llm.assistant_start}Summary:"

    def render_as_chat(self, llm: LLM, header: str = ""):
        return f"{self.render_task_as_chat(llm=llm, header=header)} {self.summary}{llm.assistant_end}"


class Summarize(Template):
    template = env.from_string(
        """\
{{ llm.system_start -}}
{{ system_prompt }}
{{- llm.system_end }}

{{llm.user_start}}{{explanation}}{{llm.user_end}}
{% for example in examples %}
{{example}}
{% endfor %}
{{task}}
"""
    )

    explanation = """\
Given a passage of text, write a summary of the passage. \
Include key points, important details, and salient information. \
Do not write anything other than the summary."""

    @classmethod
    def render(
        cls,
        llm: LLM,
        passage: str,
        system_prompt: str | None = None,
        examples: list[Summary] | None = None,
    ) -> str:
        if examples is None:
            examples = []
        system_prompt = system_prompt or llm.default_system_prompt
        examples_ = [
            e.render_as_chat(llm=llm, header=f"--- Example {i+1} ---\n")
            for i, e in enumerate(examples)
        ]
        task = Summary(passage=passage, summary="").render_task_as_chat(
            llm=llm, header="--- Task ---\n"
        )
        return cls.template.render(
            system_prompt=system_prompt,
            explanation=cls.explanation,
            task=task,
            examples=examples_,
            llm=llm,
        )


class SummarizeWithContext(Summarize):
    explanation = """Given a passage of text and a paragraph of context for that passage, \
write a summary of the passage. Include key points, important details, and \
make use of the context where necessary. \
Do not write anything other than the summary."""

    @classmethod
    def render(
        cls,
        llm: LLM,
        context: str,
        passage: str,
        system_prompt: str | None = None,
        examples: list[SummaryWithContext] | None = None,
    ) -> str:
        if examples is None:
            examples = []
        system_prompt = system_prompt or llm.default_system_prompt
        examples_ = [
            e.render_as_chat(llm=llm, header=f"--- Example {i+1} ---\n")
            for i, e in enumerate(examples)
        ]
        task = Summary(
            passage=passage, context=context, summary=""
        ).render_task_as_chat(llm=llm, header="--- Task ---\n")
        return cls.template.render(
            system_prompt=system_prompt,
            explanation=cls.explanation,
            task=task,
            examples=examples_,
            llm=llm,
        )


# import guidance
# from functools import partial

# class SummarizeGuidance(Template):
#     template = """\
# {{#system~}}
# {{system_prompt}}
# {{~/system}}

# {{~! EXPLAIN THE SUMMARIZATION TASK ~}}
# {{#user~}}
# Given a passage of text, write a summary of the passage. \
# Include key points, important details, and salient information. \
# Do not write anything other than the summary.\
# {{~#if examples}}{{/user}}{{/if}}

# {{~! EXPLAIN THE SUMMARIZATION TASK ~}}
# {{~#each examples}}
# {{#user~}}
# Passage: {{this.passage}}
# {{~/user}}

# {{#assistant~}}
# Summary: {{this.summary}}
# {{~/assistant}}
# {{~/each}}
# {{~#if examples}}{{#user}}{{/if}}

# {{~! TASK ~}}
# --- Task ---
# Passage: {{passage}}
# {{~/user}}

# {{~! GENERATE SUMMARY}}\
# {{#assistant~}}
# Summary: {{gen "summary" temperature=0.8 max_tokens=256 top_p=0.95}}
# {{~/assistant}}\
# """

#     @classmethod
#     def program(
#         cls,
#         llm: LLM,
#         passage: str,
#         system_prompt: str | None = None,
#         examples: list[Summary] | None = None,
#     ) -> guidance.Program:
#         if examples is None:
#             examples = []
#         system_prompt = SystemPrompt.render(llm=llm, prompt=system_prompt)
#         prog = guidance(cls.guidance_program)
#         return partial(
#             prog,
#             system_prompt=system_prompt,
#             examples=examples,
#             passage=passage,
#             llm=llm,
#             explanation=cls.explanation,
#         )
