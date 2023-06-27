from clonr.llms import LLM, OpenAI, LlamaCpp, MockLLM
from clonr.templates.base import env, Template


# Given an observation, rate the significance of it
class MemoryRating(Template):
    template = env.from_string(
        """\
{{ llm.system_start -}}
{{ system_prompt }}
{{- llm.system_end }}

{{ llm.user_start -}}\
Given the following memory, rate the significance of that memory. \
Use a scale of 0 to 9, where 0 is purely mundane (e.g., brushing teeth, making bed) \
and 9 is extremely poignant (e.g., a break up, college acceptance). \
Rate the likely poignancy of the following piece of memory. \
Respond with a single integer.
{{- llm.user_end }}

{{ llm.user_start -}}
--- Example 1 ---
Memory: I cleaned up my room.
{{- llm.user_end }}

{{ llm.assistant_start -}}
Rating: 1
{{- llm.assistant_end }}

{{ llm.user_start -}}
--- Example 2 ---
Memory: I asked out my crush on a date.
{{- llm.user_end }}

{{ llm.assistant_start -}}
Rating: 7
{{- llm.assistant_end }}

{{ llm.user_start -}}
--- Task ---
Memory: {{ memory }}
{{- llm.user_end }}

{{ llm.assistant_start -}}
Rating: \
"""
    )

    @classmethod
    def render(
        cls,
        llm: LLM,
        memory: str,
        system_prompt: str | None = None,
    ):
        if system_prompt is None:
            system_prompt = llm.default_system_prompt
        return cls.template.render(llm=llm, system_prompt=system_prompt, memory=memory)

    @classmethod
    def get_constraints(cls, llm):
        """WARNING: This is hacky and not robust. I had to change from 0-9 so that everthing
        is a 1 token generation. In order to generate something like 10, the problem is that we are
        using logits_bias to try to guide >1 tokens in advance. There are multiple
        problems here.
        1. We don't have token healing (so we can't figure out ' A' vs 'A' when a
        space is needed)
        2. Beyond one token we're screwed
        3. [less problematic] Partial completions are ignored ['Par', 'is'] will not be
        an option for ['Paris']
        4. This can easily break when tokenizers change, there is nothing keeping this in sync!

        Thankfully, for gpt-3.5, the digits 1 through 10 inclusive are all individual tokens.
        For LlamaCPP, only 1-9 are tokens, so we have to generate twice and then filter.

        Also note that no digits have a space prefix. OpenAI also has a second version of digits in coding font
        """
        # we have to use type, since we don't want to match a subclass
        if type(llm) == LlamaCpp:
            ids = [
                31852,
                31853,
                31855,
                31878,
                31882,
                31880,
                31887,
                31888,
                31886,
                31877,
            ]
        elif type(llm) in (OpenAI, MockLLM):
            ids = [15, 16, 17, 18, 19, 20, 21, 22, 23, 24]
        else:
            raise ValueError(f"The llm type: {type(llm)} is not supported.")
        max_tokens = 1
        logit_bias = {x: 100 for x in ids}
        return dict(logit_bias=logit_bias, max_tokens=max_tokens, temperature=0.0)


class MemoryRatingWithContext(MemoryRating):
    template = env.from_string(
        """\
{{ llm.system_start -}}
{{ system_prompt }}
{{- llm.system_end }}

{{ llm.user_start -}}\
Given the following memory, along with a paragraph describing the  \
context in which the memory was formed, rate the significance of that memory. \
Use a scale of 0 to 9, where 0 is purely mundane (e.g., brushing teeth, making bed) \
and 9 is extremely poignant (e.g., a break up, college acceptance). If the context \
is relevant to rating the memory (e.g. if the context is "I have not showered in two months", \
then the rating of the memory "I showered" will be higher). \
Rate the likely poignancy of the following piece of memory. \
Respond with a single integer.
{{- llm.user_end }}

{{ llm.user_start -}}
--- Example 1 ---
Context: I got home from a long day of school, but I am happy because I scored 95% on my geometry test.
Memory: I cleaned up my room.
{{- llm.user_end }}
{{ llm.assistant_start -}}
Rating: 1
{{- llm.assistant_end }}

{{ llm.user_start -}}
--- Example 2 ---
Context: I just arrived home from my study abroad trip, and I can't wait to finally \
eat my mother's home cooking.
Memory: My mom cooked dinner for me.
{{- llm.user_end }}
{{ llm.assistant_start -}}
Rating: 5
{{- llm.assistant_end }}

{{ llm.user_start -}}
--- Task ---
Context: {{ context }}
Memory: {{ memory }}
{{- llm.user_end }}
{{ llm.assistant_start -}}
Rating: \
"""
    )

    @classmethod
    def render(
        cls,
        llm: LLM,
        memory: str,
        context: str,
        system_prompt: str | None = None,
    ):
        if system_prompt is None:
            system_prompt = llm.default_system_prompt
        return cls.template.render(
            llm=llm, system_prompt=system_prompt, memory=memory, context=context
        )
