import datetime
import random
import re
import uuid
from typing import Annotated

from fastapi_users.schemas import BaseUser, BaseUserCreate, BaseUserUpdate
from pydantic import (
    AfterValidator,
    BaseModel,
    ConfigDict,
    EmailStr,
    Field,
    ValidationInfo,
    model_validator,
)

from app.clone.types import AdaptationStrategy, InformationStrategy, MemoryStrategy
from clonr.utils import get_current_datetime


def special_char_validator(v: str | None, info: ValidationInfo) -> str | None:
    if v is None:
        return v
    if "<|" in v or "|>" in v:
        raise ValueError("May not contain special chars <| or |>")
    return v


# NOTE (Jonny): I forgot that this one is important, we don't want to allow users to
# do like llm-injection
def sanitize_text(text: str):
    return re.sub(r"\<\|.*?\|\>", "", text)


def text_sanitation_validator(v: str | None, info: ValidationInfo) -> str | None:
    if v is None:
        return v
    return sanitize_text(v)


def generate_hex_code():
    s = "1234567890ABCDEF"
    return "".join(random.choice(s) for _ in range(6))


def validate_hex_code(s: str | None):
    if s is None:
        return True
    if not all(x in "1234567890ABCDEFabcdef" for x in s):
        raise ValueError(f"Invalid hexcode: {s}")
    return s


class UserRead(BaseUser[uuid.UUID]):
    model_config = ConfigDict(from_attributes=True)

    private_chat_name: str
    is_banned: bool
    nsfw_enabled: bool
    num_free_messages_sent: int


class UserCreate(BaseUserCreate):
    pass


class UserUpdate(BaseUserUpdate):
    private_chat_name: Annotated[str, AfterValidator(special_char_validator)] = Field(
        default=None,
        min_length=1,
        max_length=32,
    )


class CommonMixin(BaseModel):
    id: uuid.UUID
    created_at: datetime.datetime
    updated_at: datetime.datetime


class CreatorCreate(BaseModel):
    username: str = Field(
        description="username must be 3 <= len(name) <= 20 characters, start with a letter and only contain hyphens and underscores",
        pattern=r"^[a-zA-Z][a-zA-Z0-9_\-]{2,29}$",
    )
    is_public: bool = False


class CreatorPatch(BaseModel):
    username: str | None = Field(
        default=None,
        pattern=r"^[a-zA-Z][a-zA-Z0-9_]{2,29}$",
    )
    is_active: bool | None = None


class Creator(CreatorCreate):
    model_config = ConfigDict(from_attributes=True)

    user_id: uuid.UUID
    is_active: bool
    is_public: bool
    created_at: datetime.datetime
    updated_at: datetime.datetime


class TagCreate(BaseModel):
    name: str
    color_code: Annotated[str, AfterValidator(validate_hex_code)] = Field(
        default_factory=generate_hex_code,
        detail="Color hex code for displaying tag on the frontend",
    )


class TagUpdate(BaseModel):
    name: str | None = None
    color_code: Annotated[str | None, AfterValidator(validate_hex_code)] = Field(
        default=None,
        detail="Color hex code for displaying tag on the frontend",
    )


class Tag(BaseModel):
    id: int
    created_at: datetime.datetime
    updated_at: datetime.datetime
    name: str
    color_code: str


class CloneCreate(BaseModel):
    name: Annotated[str, AfterValidator(special_char_validator)] = Field(min_length=2)
    short_description: Annotated[str, AfterValidator(special_char_validator)] = Field(
        min_length=3
    )
    long_description: Annotated[
        str | None, AfterValidator(text_sanitation_validator)
    ] = Field(default=None, min_length=32)
    greeting_message: Annotated[
        str | None, AfterValidator(special_char_validator)
    ] = None
    avatar_uri: str | None = None
    is_active: bool = True
    is_public: bool = False
    is_short_description_public: bool = True
    is_long_description_public: bool = False
    is_greeting_message_public: bool = True
    tags: list[int] | None = None


class CloneUpdate(BaseModel):
    # If we let creators change the name once there are already active conversations, that could be bad.
    # name: Annotated[str | None, AfterValidator(special_char_validator)] = None
    short_description: Annotated[
        str | None, AfterValidator(special_char_validator)
    ] = None
    long_description: Annotated[
        str | None, AfterValidator(text_sanitation_validator)
    ] = None
    greeting_message: Annotated[
        str | None, AfterValidator(special_char_validator)
    ] = None
    avatar_uri: str | None = None
    is_active: bool | None = None
    is_public: bool | None = None
    is_short_description_public: bool | None = None
    is_long_description_public: bool | None = None
    is_greeting_message_public: bool | None = None
    tags: list[int] | None = None


# NOTE (Jonny): have to duplicate the code since Liskov sub error says Tags can't change the inherited list[str] return type
class Clone(CommonMixin):
    model_config = ConfigDict(from_attributes=True)

    name: Annotated[str, AfterValidator(special_char_validator)] = Field(min_length=2)
    short_description: Annotated[str, AfterValidator(special_char_validator)] = Field(
        min_length=3
    )
    long_description: Annotated[
        str | None, AfterValidator(text_sanitation_validator)
    ] = Field(default=None, min_length=32)
    greeting_message: Annotated[
        str | None, AfterValidator(special_char_validator)
    ] = None
    avatar_uri: str | None = None
    is_active: bool = True
    is_public: bool = False
    is_short_description_public: bool = True
    is_long_description_public: bool = False
    is_greeting_message_public: bool = True
    creator_id: uuid.UUID
    num_messages: int
    num_conversations: int
    tags: list[Tag]


class CloneSearchResult(CommonMixin, BaseModel):
    model_config = ConfigDict(from_attributes=True)

    creator_id: uuid.UUID
    name: str
    short_description: str | None
    long_description: str | None
    avatar_uri: str | None = (
        None  # TODO (Jonny) make sure we don't throw errors here and un None it
    )
    num_messages: int
    num_conversations: int
    tags: list[Tag]


# TODO (Jonny): we need to take in more information than just content
# like accepting character names, URLs, etc. Maybe we feed these back to
# the user, and have them accept them.
# TODO (Jonny): URL field is unused until we figure out a way to make it safe
# See the bottom for some sample validation code
class DocumentCreate(BaseModel):
    content: Annotated[str, AfterValidator(text_sanitation_validator)]
    name: str | None = Field(
        max_length=36,
        description="A human readable name for the document. If none is given, one will be automatically assigned.",
    )
    description: str | None = Field(
        max_length=128, description="A short description of the document"
    )
    type: Annotated[str, AfterValidator(special_char_validator)] = Field(
        max_length=32,
        pattern=r"[a-zA-Z0-9_\-]+",
        description="One word tag describing the source. Letters, numbers, underscores, and hyphens allowed.",
    )
    url: str | None = Field(
        max_length=256, description="The resource URL if applicable", default=None
    )
    # Only list is allowed right now
    # index_type: IndexType = Field(
    #     default=IndexType.list, description="The type of index to build."
    # )


# we don't allow updates on the other fields. URL, content, and type are packaged together
# and it'd be too complicated to allow updating these. It's better to just create a new doc
class DocumentUpdate(BaseModel):
    name: str | None = None
    description: str | None = None
    type: str | None = None


class Document(CommonMixin, DocumentCreate):
    model_config = ConfigDict(from_attributes=True)

    clone_id: uuid.UUID


class DocumentSuggestion(BaseModel):
    title: str = Field(
        description="The title of the found page. Often will be the character name."
    )
    url: str | None = Field(default=None, description="The url of the found resource.")
    thumbnail_url: str | None = Field(
        default=None,
        description="A URL pointing to a page preview of the suggested resource.",
    )


class MonologueCreate(BaseModel):
    content: Annotated[str, AfterValidator(text_sanitation_validator)] = Field(
        description="An example message that your clone might send. If you clone sends short replies, this should be short. If your clone is long winded, it can be multiple sentences."
    )
    source: str = Field(
        default="manual",
        description="Where the quote was taken from. Manual, wikiquotes are the two options",
    )


class MonologueUpdate(BaseModel):
    content: Annotated[str | None, AfterValidator(text_sanitation_validator)] = None
    source: str | None = None


class Monologue(CommonMixin, MonologueCreate):
    model_config = ConfigDict(from_attributes=True)

    clone_id: uuid.UUID


# TODO (Jonny): add timezone to this! fix the timezone for all messages at convo create time.
# we're getting a mismatch in times between user and assistant for some reason too
# lol maybe don't add it: https://www.youtube.com/watch?v=-5wpm-gesOY.
class ConversationCreate(BaseModel):
    name: str | None = Field(
        default=None,
        description="A name to assign to the conversation to later remember it.",
    )
    user_name: Annotated[str | None, AfterValidator(special_char_validator)] = Field(
        default=None,
        min_length=1,
        max_length=32,
        description="The display name that the user wants to use for the conversation. This cannot be changed once you start the conversation. If your user name collides with the clone name, then an additional digit will be added",
    )
    memory_strategy: MemoryStrategy = Field(
        default=MemoryStrategy.zero,
        description="Whether to turn off memory (old messages removed at context length limit), use short-term memory, or use the advanced Clonr long-term memory",
    )
    information_strategy: InformationStrategy = Field(
        default=InformationStrategy.internal,
        description="The level of factual accuracy to give your bot. Internal enables creator knowledge sources. External allows for pulling information on current events.",
    )
    adaptation_strategy: AdaptationStrategy | None = Field(
        default=None,
        description="How flexible the clone is on changing its long description. Static means never chaning. Fluid means completely adaptive. Dynamic means partial adaption.",
    )
    clone_id: uuid.UUID = Field(description="The clone that a user will chat with")

    @model_validator(mode="after")
    def check_adaptation_agrees_with_memory(self) -> "ConversationCreate":
        if self.memory_strategy != MemoryStrategy.long_term:
            if self.adaptation_strategy is not None:
                raise ValueError(
                    "Adaptation strategies are only available with long-term memory"
                )
        elif self.adaptation_strategy is None:
            raise ValueError(
                "Adaptation strategy must be set when using long-term memory."
            )
        return self


class ConversationUpdate(BaseModel):
    name: str | None = None
    is_active: bool | None = Field(
        default=None, description="Wether to archive the conversation or not."
    )


class Conversation(CommonMixin, ConversationCreate):
    model_config = ConfigDict(from_attributes=True)

    user_id: uuid.UUID = Field(description="The user that will chat with this clone")
    is_active: bool
    clone_id: uuid.UUID
    num_messages_ever: int
    last_message: str | None
    clone_name: str


class ConversationInSidebar(Conversation):
    rank: int
    group_updated_at: datetime.datetime


class ConversationWithMessages(Conversation):
    messages: list["Message"]


# NOTE (Jonny): We don't allow users to change outputs of the clones, so is_clone.
# is not a provided argument. sender_name, clone_id, and conversation_id can be inferred
# from the user, convo, and path respectively
class MessageCreate(BaseModel):
    content: Annotated[str, AfterValidator(special_char_validator)] = Field(
        description="Message content. Messages may not contain <| or |>.",
        max_length=1600,
    )


class MessageUpdate(BaseModel):
    is_active: bool


class Message(CommonMixin, MessageCreate):
    model_config = ConfigDict(from_attributes=True)

    sender_name: str
    timestamp: datetime.datetime
    is_clone: bool
    is_main: bool
    is_active: bool
    parent_id: uuid.UUID | None
    clone_id: uuid.UUID
    user_id: uuid.UUID
    conversation_id: uuid.UUID


class MessageGenerate(BaseModel):
    is_revision: bool = Field(
        default=False,
        description="Whether the current request is to revise a previous generation, or create a new one.",
    )


# user_id is taken from auth, and clone_id is taken from the route.
class SharedMemoryCreate(BaseModel):
    content: Annotated[str, AfterValidator(special_char_validator)] = Field(
        detail="The memory that your clone will record. In general, the format should be stuff like: 'I felt angry' or 'I saw a duck'"
    )
    timestamp: datetime.datetime = Field(
        default_factory=get_current_datetime,
        detail="The timestamp at which this memory occurred. Defaults to current time.",
    )
    importance: int | None = Field(
        default=None,
        detail="The importance to assign to this memory. If none is set, one will be computed automatically.",
    )


class LongDescription(CommonMixin, BaseModel):
    content: str
    clone_id: uuid.UUID
    documents: list[Document]


class CreatorPartnerProgramSignupCreate(BaseModel):
    email: EmailStr = Field(
        description="An email with which Clonr can notify you when you can sign up for the Partner Program"
    )
    nsfw: bool | None = Field(default=None, description="Intends to create NSFW clones")
    personal: bool | None = Field(
        default=None, description="Intends to create clones for personal use"
    )
    quality: bool | None = Field(
        default=None,
        description="Intends to create clones with high quality or fidelity",
    )
    story: bool | None = Field(
        default=None,
        description="Intends to create story-based bots, short or long form content.",
    )
    roleplay: bool | None = Field(
        default=None, description="Intends to create roleplay scenarios"
    )


class CreatorPartnerProgramSignup(CommonMixin, CreatorPartnerProgramSignupCreate):
    model_config = ConfigDict(from_attributes=True)

    user_id: uuid.UUID


class ClonrPlusSignupCreate(BaseModel):
    email: EmailStr = Field(
        description="An email with which Clonr can notify you when you can purchase the presale for Clonr+"
    )
    nsfw: bool | None = Field(
        default=None, description="Signing up because of NSFW access"
    )
    long_term_memory: bool | None = Field(
        default=None,
        description="Signing up because of long term memory and long chats",
    )
    greater_accuracy: bool | None = Field(
        default=None, description="Signing up because of greater clone accuracy"
    )
    multiline_chat: bool | None = Field(
        default=None, description="Signing up because of multiline chat feature"
    )


class ClonrPlusSignup(CommonMixin, ClonrPlusSignupCreate):
    model_config = ConfigDict(from_attributes=True)

    user_id: uuid.UUID
