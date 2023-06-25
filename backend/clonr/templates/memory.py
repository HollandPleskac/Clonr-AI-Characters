from clonr.llms import LLM
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
Use a scale of 1 to 10, where 1 is purely mundane (e.g., brushing teeth, making bed) \
and 10 is extremely poignant (e.g., a break up, college acceptance). \
Rate the likely poignancy of the following piece of memory. \
Respond with a single integer. Let's try two examples.
{{- llm.user_end }}

{{ llm.user_start -}}
--- Example 1 ---
Memory: I brushed my teeth before bed.
{{- llm.user_end }}
{{ llm.assistant_start -}}
Score: 1
{{- llm.assistant_end }}

{{ llm.user_start -}}
--- Example 2 ---
Memory: I got married.
{{- llm.user_end }}
{{ llm.assistant_start -}}
Score: 10
{{- llm.assistant_end }}

{{ llm.user_start -}}
--- Task ---
Memory: {{ memory }}
{{- llm.user_end }}
{{ llm.assistant_start -}}
Score: {{- llm.assistant_end }}\
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


# Retrieve most salient questions for reflection
class ReflectionRetrieval:
    template = env.from_string(
        """\
{#### SYSTEM PROMPT ####}\
{{ llm.system_start -}}
{{ system_prompt }}
{{- llm.system_end }}

{#### USER START ####}\
{{ llm.user_start -}}\

{#### RECENT MEMORIES ####}
Recent memories: {{ recent_memories }} 
\

{#### EXPLAIN THE REFLECTION RETRIEVAL TASK ####}\
Given only the information above on recent memories, what are 3 most salient high-level questions we can answer about the subjects in the statements? \
\

{{- llm.user_end }}

{{ llm.assistant_start -}}\
"""
    )

    @classmethod
    def render(
        cls,
        llm: LLM,
        memories: str,
        system_prompt: str | None = None,
    ):
        if system_prompt is None:
            system_prompt = llm.default_system_prompt
        return cls.template.render(
            llm=llm, system_prompt=system_prompt, memories=memories
        )


# Generate actual reflections / insights based on retrieved salient memories
class ReflectionGeneration:
    template = env.from_string(
        """\
{#### SYSTEM PROMPT ####}\
{{ llm.system_start -}}
{{ system_prompt }}
{{- llm.system_end }}

{#### USER START ####}\
{{ llm.user_start -}}\

{#### RELEVANT MEMORIES ####}
Relevant memories: {{ relevant_memories }}
\

{#### EXPLAIN THE REFLECTION GENERATION TASK ####}\
What 5 high-level insights can you infer from the above statements of relevant memories? \
\

{{- llm.user_end }}

{{ llm.assistant_start -}}\
"""
    )

    @classmethod
    def render(
        cls,
        llm: LLM,
        relevant_memories: str,
        system_prompt: str | None = None,
    ):
        if system_prompt is None:
            system_prompt = llm.default_system_prompt
        return cls.template.render(
            llm=llm, system_prompt=system_prompt, relevant_memories=relevant_memories
        )
