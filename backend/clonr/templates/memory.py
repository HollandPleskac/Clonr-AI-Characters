from pydantic import BaseModel

from clonr.data_structures import Memory
from clonr.llms import LLM, LlamaCpp, MockLLM, OpenAI
from clonr.templates.base import Template, env


class MemoryExample(BaseModel):
    memory: str
    rating: int


class MemoryExampleWithContext(MemoryExample):
    context: str


DEFAULT_MEMORY_RATING_EXAMPLES = [
    MemoryExample(memory="I cleaned up my room.", rating=1),
    MemoryExample(memory="I asked my crush out on a date", rating=7),
]


DEFAULT_MEMORY_RATING_WITH_CONTEXT_EXAMPLES = [
    MemoryExampleWithContext(
        memory="I cleaned up my room.",
        context="I've been thinking a lot about what I want to do after graduation. I like cooking, but I'm not sure if I want to go to culinary school",
        rating=1,
    ),
    MemoryExampleWithContext(
        memory="I took a shower",
        context="I haven't showered in almost a month, and people have begun to notice. I can't wait until I get to the hotel, where I can finally shower",
        rating=4,
    ),
]


# Given an observation, rate the significance of it
class MemoryRating(Template):
    chat_template = env.from_string(
        """\
{{ llm.system_start -}}
{{ system_prompt }}
{{- llm.system_end }}

{{ llm.user_start -}}\
Given a memory, rate the significance of that memory. \
Use a scale of 0 to 9, where 0 is purely mundane (e.g., brushing teeth, making bed) \
and 9 is extremely poignant (e.g., a break up, college acceptance). \
Rate the likely poignancy of the following memory, given in the format
MEMORY: <memory>.
Respond with a single integer in the format:
RATING: <rating>.
{% if (examples) %}
Let's try a few examples.
{{- llm.user_end }}
{% for e in examples %}
{{ llm.user_start -}}
MEMORY: {{ e.memory }}
{{- llm.user_end }}

{{ llm.assistant_start -}}
RATING: {{ e.rating }}
{{- llm.assistant_end }}
{% endfor %}
{{- llm.user_start  }}
{%- endif %}
{{ llm.user_start -}}
Now rate the following memory.
MEMORY: {{memory}}
{{- llm.user_end }}

{{ llm.assistant_start -}}
RATING: \
{{ llm.assistant_end }}
"""
    )
    instruct_template = env.from_string(
        """\
Below is an instruction that describes a task. Write a response that \
appropriately completes the request

### Instruction: 
Given a memory, rate the significance of that memory. \
Use a scale of 0 to 9, where 0 is purely mundane (e.g., brushing teeth, making bed) \
and 9 is extremely poignant (e.g., a break up, college acceptance). \
Rate the likely poignancy of the following memory, given in the format
MEMORY: <memory>.
Respond with a single integer in the format:
RATING: <rating>.
{% if (examples) %}
Let's try a few examples.
{% for e in examples %}
MEMORY: {{ e.memory }}
RATING: {{ e.rating }}
{%- if not loop.last %}
{% endif %}
{% endfor %}
{%- endif %}
Now rate the following memory.
MEMORY: {{memory}}

### Response:
RATING: \
"""
    )

    @classmethod
    def render(
        cls,
        llm: LLM,
        memory: str,
        examples: list[MemoryExample] | None = None,
        system_prompt: str | None = None,
    ):
        if system_prompt is None:
            system_prompt = llm.default_system_prompt
        if examples is None:
            examples = DEFAULT_MEMORY_RATING_EXAMPLES
        return cls.chat_template.render(
            llm=llm, system_prompt=system_prompt, memory=memory, examples=examples
        )

    @classmethod
    def render_instruct(cls, memory: str, examples: list[MemoryExample] | None = None):
        if examples is None:
            examples = DEFAULT_MEMORY_RATING_EXAMPLES
        return cls.instruct_template.render(memory=memory, examples=examples)

    @classmethod
    def get_constraints(cls, llm: LLM):
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
            # this changed for llama-2 it seems, it used to be in the 30,000s.
            if "ggml" in llm.model:
                # this is for llama2 llama-cpp
                ids = [
                    29900,
                    29896,
                    29906,
                    29941,
                    29946,
                    29945,
                    29953,
                    29955,
                    29947,
                    29929,
                ]
            else:
                # this is for llama2 huggingface
                ids = [
                    29896,
                    29906,
                    29941,
                    29946,
                    29945,
                    29953,
                    29955,
                    29947,
                    29929,
                    29900,
                ]
        elif type(llm) in (OpenAI, MockLLM):
            ids = [15, 16, 17, 18, 19, 20, 21, 22, 23, 24]
        else:
            raise ValueError(f"The llm type: {type(llm)} is not supported.")
        max_tokens = 1
        logit_bias = {x: 100 for x in ids}
        return dict(logit_bias=logit_bias, max_tokens=max_tokens, temperature=0.0)


class MemoryRatingWithContext:
    chat_template = env.from_string(
        """\
{{ llm.system_start -}}
{{ system_prompt }}
{{- llm.system_end }}

{{ llm.user_start -}}\
Given a memory, \
along with a paragraph describing the context in which the memory was formed, \
rate the significance of that memory. \
Use a scale of 0 to 9, where 0 is purely mundane (e.g., brushing teeth, making bed) \
and 9 is extremely poignant (e.g., a break up, college acceptance). \
Rate the likely poignancy of the following piece of memory, given in the format
CONTEXT: <context>.
MEMORY: <memory>.
Respond with a single integer in the format:
RATING: <rating>.
{% if (examples) %}
Let's try a few examples.
{{- llm.user_end }}
{% for e in examples %}
{{ llm.user_start -}}
CONTEXT: {{ e.context }}
MEMORY: {{ e.memory }}
{{- llm.user_end }}

{{ llm.assistant_start -}}
RATING: {{ e.rating }}
{{- llm.assistant_end }}
{% endfor %}
{{- llm.user_start  }}
{%- endif %}
{{ llm.user_start -}}
Now rate the following memory.
CONTEXT: {{context}}
MEMORY: {{memory}}
{{- llm.user_end }}

{{ llm.assistant_start -}}
RATING: \
{{ llm.assistant_end }}
"""
    )
    instruct_template = env.from_string(
        """\
Below is an instruction that describes a task. Write a response that \
appropriately completes the request

### Instruction: 
Given a memory, \
along with a paragraph describing the context in which the memory was formed, \
rate the significance of that memory. \
Use a scale of 0 to 9, where 0 is purely mundane (e.g., brushing teeth, making bed) \
and 9 is extremely poignant (e.g., a break up, college acceptance). \
Rate the likely poignancy of the following piece of memory, given in the format
CONTEXT: <context>.
MEMORY: <memory>.
Respond with a single integer in the format:
RATING: <rating>.
{% if (examples) %}
Let's try a few examples.
{% for e in examples %}
CONTEXT: {{ e.context }}
MEMORY: {{ e.memory }}
RATING: {{ e.rating }}
{%- if not loop.last %}
{% endif %}
{% endfor %}
{%- endif %}

Now rate the following memory.
CONTEXT: {{context}}
MEMORY: {{memory}}

### Response:
RATING: \
"""
    )

    @classmethod
    def render(
        cls,
        llm: LLM,
        memory: str | Memory,
        examples: list[MemoryExampleWithContext] | None = None,
        system_prompt: str | None = None,
    ):
        if system_prompt is None:
            system_prompt = llm.default_system_prompt
        if examples is None:
            examples = DEFAULT_MEMORY_RATING_WITH_CONTEXT_EXAMPLES
        if isinstance(memory, Memory):
            memory = memory.content
        return cls.chat_template.render(
            llm=llm, system_prompt=system_prompt, memory=memory, examples=examples
        )

    @classmethod
    def render_instruct(
        cls,
        memory: str | Memory,
        examples: list[MemoryExampleWithContext] | None = None,
    ):
        if isinstance(memory, Memory):
            memory = memory.content
        if examples is None:
            examples = DEFAULT_MEMORY_RATING_WITH_CONTEXT_EXAMPLES
        return cls.instruct_template.render(memory=memory, examples=examples)

    @classmethod
    def get_constraints(cls, llm: LLM):
        return MemoryRating.get_constraints(llm=llm)
