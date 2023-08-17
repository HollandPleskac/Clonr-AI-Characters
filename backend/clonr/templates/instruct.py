from clonr.llms import LLM, GenerationParams

from .base import Template, env


class SingleInstructionChat(Template):
    template = env.from_string(
        """\
{%- if (system_prompt) -%}
{{ llm.system_start -}}
{{ system_prompt }}
{{- llm.system_end }}
{%- endif %}

{{- llm.user_start -}}
Below is an instruction that describes a task. Write a response that appropriately completes the request.

### Instruction:
{{ instruction }}
{{- llm.user_end }}

{{ llm.assistant_start -}}
### Response:
{{- llm.assistant_end }}
"""
    )

    default_gen_params = GenerationParams(
        temperature=0.8, top_p=0.95, frequency_penalty=0.2, max_tokens=256
    )

    @classmethod
    def render(
        cls,
        llm: LLM,
        instruction: str,
        system_prompt: str | None = None,
    ) -> str:
        return cls.template.render(
            llm=llm,
            instruction=instruction,
            system_prompt=system_prompt,
        ).lstrip()


class SingleInstruction(SingleInstructionChat):
    template = env.from_string(
        """\
Below is an instruction that describes a task. Write a response that appropriately completes the request.

### Instruction:
{{ instruction }}

### Response:\
"""
    )


# class SingleInstructionGuidanceChat:
#     template = """\
# {{~#if (system_prompt)~}}
# {{#system~}}
# {{system_prompt}}
# {{~/system}}
# {{~/if}}

# {{~! INSTRUCTION START ~}}
# {{~#user~}}
# Below is an instruction that describes a task. Write a response that appropriately completes the request.

# ### Instruction:
# {{instruction}}
# {{~/user}}

# {{~! RESPONSE START ~}}
# {{#assistant~}}
# ### Response:
# {{gen "response" GEN_PARAMS}}
# {{~/assistant}}
# """

# class SingleInstructionGuidance(SingleInstructionGuidanceChat):
#     template = """\
# Below is an instruction that describes a task. Write a response that appropriately completes the request.

# ### Instruction:
# {{instruction}}

# ### Response:
# {{gen "response" GEN_PARAMS}}"""
