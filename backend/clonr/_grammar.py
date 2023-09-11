from typing import TypedDict

import pyparsing as pp


class MessageDict(TypedDict):
    role: str
    content: str


LLM_SYSTEM_ROLE = "system"
LLM_ASSISTANT_ROLE = "assistant"
LLM_USER_ROLE = "user"

DIALOGUE_CHARACTER_ROLE = "char"
DIALOGUE_USER_ROLE = "user"


# DialogueChunk grammar
_dialogue_lbrace = pp.LineStart() + pp.Literal("{{").suppress()
_dialogue_rbrace = pp.Literal("}}:").suppress()
_dialogue_role = (pp.Keyword(DIALOGUE_USER_ROLE) | pp.Keyword(DIALOGUE_CHARACTER_ROLE))(
    "role"
)
_dialogue_key = _dialogue_lbrace + _dialogue_role + _dialogue_rbrace
content = pp.originalTextFor(pp.SkipTo(_dialogue_key | pp.stringEnd(), include=False))(
    "content"
)
_dialogue_message = _dialogue_key + content
_dialogue_message.setParseAction(
    lambda x: {"role": x.role, "content": x.content.strip()}
)
_dialogue_chunk_parser = pp.OneOrMore(_dialogue_message)


# NOTE: this will allow things other than user and char to appear inside of {{}}
# maybe we should make a hard check for this?
def parse_dialogue_chunk(dialogue_chunk: str) -> list[MessageDict]:
    return _dialogue_chunk_parser.parse_string(dialogue_chunk).as_list()


# LLM prompt grammar
_llm_message_start = pp.Literal("<|im_start|>").suppress()
_llm_message_end = pp.Literal("<|im_end|>").suppress()
_llm_role = (
    pp.Keyword(LLM_USER_ROLE)
    | pp.Keyword(LLM_ASSISTANT_ROLE)  # noqa
    | pp.Keyword(LLM_SYSTEM_ROLE)  # noqa
)("role")
_llm_content = pp.SkipTo(_llm_message_end | pp.stringEnd())("content")
_llm_message = _llm_message_start + _llm_role + _llm_content + _llm_message_end
_llm_message.setParseAction(lambda x: dict(role=x.role, content=x.content.strip()))
_llm_prompt_parser = pp.OneOrMore(_llm_message)


def parse_prompt(prompt: str) -> list[MessageDict]:
    return _llm_prompt_parser.parse_string(prompt, parse_all=True).as_list()
