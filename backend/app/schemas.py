import datetime
import random
import uuid
from typing import Annotated

from fastapi_users.schemas import BaseUser, BaseUserCreate, BaseUserUpdate
from pydantic import (
    AfterValidator,
    BaseModel,
    ConfigDict,
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


def generate_hex_code():
    s = "1234567890ABCDEF"
    return "".join(random.choice(s) for _ in range(6))


def is_valid_hex_code(s: str | None):
    if s is None:
        return True
    return all(x in "1234567890ABCDEF" for x in s)


class UserRead(BaseUser[uuid.UUID]):
    model_config = ConfigDict(from_attributes=True)

    private_chat_name: str
    is_banned: bool
    nsfw_enabled: bool
    num_free_messages_sent: int
    is_subscribed: bool


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


class CreatorPatch(CreatorCreate):
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
    color_code: Annotated[str, AfterValidator(is_valid_hex_code)] = Field(
        default=generate_hex_code,
        detail="Color hex code for displaying tag on the frontend",
    )


class TagUpdate(TagCreate):
    name: str | None = None
    color_code: Annotated[str | None, AfterValidator(is_valid_hex_code)] = Field(
        default=None,
        detail="Color hex code for displaying tag on the frontend",
    )


class Tag(CommonMixin, BaseModel):
    name: str
    color_code: str


class CloneCreate(BaseModel):
    name: str = Field(min_length=2)
    short_description: str = Field(min_length=3)
    long_description: str | None = Field(default=None, min_length=32)
    greeting_message: str | None = None
    avatar_uri: str | None = None
    is_active: bool = True
    is_public: bool = False
    is_short_description_public: bool = True
    is_long_description_public: bool = False
    is_greeting_message_public: bool = True
    tags: list[str] | None = None


class CloneUpdate(BaseModel):
    name: str | None = None
    short_description: str | None = None
    long_description: str | None = None
    greeting_message: str | None = None
    avatar_uri: str | None = None
    is_active: bool | None = None
    is_public: bool | None = None
    is_short_description_public: bool | None = None
    is_long_description_public: bool | None = None
    is_greeting_message_public: bool | None = None
    tags: list[str] | None = None


class Clone(CommonMixin, CloneCreate):
    model_config = ConfigDict(from_attributes=True)

    creator_id: uuid.UUID
    num_messages: int
    num_conversations: int
    tags: list[Tag]


class CloneSearchResult(CommonMixin, BaseModel):
    model_config = ConfigDict(from_attributes=True)

    creator_id: uuid.UUID
    name: str
    short_description: str
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
    content: str
    name: str | None = Field(
        max_length=36,
        description="A human readable name for the document. If none is given, one will be automatically assigned.",
    )
    description: str | None = Field(
        max_length=128, description="A short description of the document"
    )
    type: str | None = Field(
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
    content: str = Field(
        description="An example message that your clone might send. If you clone sends short replies, this should be short. If your clone is long winded, it can be multiple sentences."
    )
    source: str = Field(
        default="manual",
        description="Where the quote was taken from. Manual, wikiquotes are the two options",
    )


class MonologueUpdate(BaseModel):
    content: str | None = None
    source: str | None = None


class Monologue(CommonMixin, MonologueCreate):
    model_config = ConfigDict(from_attributes=True)

    clone_id: uuid.UUID


# class Flags(enum.Enum):
#     zero_memory: int
#     conversation_retrieval: int
#     information_retrieval: int
#     dynamic_quote_retrieval: int
#     internal_thought_stream: int
#     third_party_memory_stream: int
#     agent_summary_frequency: int
#     multi_character_chat__api_key_and_entity_context: int = (
#         "needs websockets, too hard now"
#     )
#     streaming_response: int = "no fuck this, too hard and not realistic"
#     multi_line_user_input: int = "would seem more realistic"
#     multi_line_clone_output: int = "a bit harder, better to just parse outputs maybe?"
#     current_event_knowledge: int = "serpAPI call"
#     NSFW: int = "no content moderation boi"


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
        default=MemoryStrategy.none,
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


# NOTE (Jonny): We don't allow users to change outputs of the clones, so is_clone.
# is not a provided argument. sender_name, clone_id, and conversation_id can be inferred from the
class MessageCreate(BaseModel):
    content: Annotated[str, AfterValidator(special_char_validator)] = Field(
        description="Message content. Messages may not contain <| or |>.",
    )
    timestamp: datetime.datetime | None = Field(
        default=None, detail="Override the current time for the message timestamp."
    )
    parent_id: uuid.UUID = Field(
        detail="The ID of the previous message in this conversation."
    )


# user_id is taken from auth, and clone_id is taken from the route.
class SharedMemoryCreate(BaseModel):
    content: str = Field(
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


class RevisionUpdate(BaseModel):
    message_id: uuid.UUID = Field(
        detail="The message being set as the chosen revision."
    )


# ------------------------------------#


# class APIKeyCreate(BaseModel):
#     user_id: uuid.UUID
#     clone_id: uuid.UUID
#     name: Optional[str] = None
#     user_id: Optional[uuid.UUID] = None


# class APIKey(CommonMixin, APIKeyCreate):
#     name: str

#     class Config:
#         orm_mode = True


# class APIKeyOnce(APIKey):
#     key: str


# class MessageCreate(BaseModel):
#     content: str
#     sender_name: str


# class Message(CommonMixin, MessageCreate):
#     from_clone: bool
#     conversation_id: uuid.UUID

#     class Config:
#         orm_mode = True


# class ConversationCreate(BaseModel):
#     clone_id: uuid.UUID
#     user_id: uuid.UUID = None
#     name: Optional[str] = None


# class Conversation(CommonMixin, ConversationCreate):
#     # This raises an error when fastapi tries to convert
#     # sqlalchemy.exc.MissingGreenlet: greenlet_spawn has not been called
#     # messages: Optional[list[Message]] = None

#     class Config:
#         orm_mode = True


# class ExampleDialogueCreate(BaseModel):
#     content: str
#     content_embedding: List[float]
#     num_tokens: int
#     summary: str
#     summary_embedding: List[float]
#     chunk_index: int
#     is_shared: bool = True
#     conversation_id: uuid.UUID


# class ExampleDialogueUpdate(ExampleDialogueCreate):
#     pass


# class ExampleDialogue(ExampleDialogueCreate):
#     class Config:
#         orm_mode = True


# class MemoryCreate(BaseModel):
#     memory: str
#     memory_embedding: List[float]
#     timestamp: datetime.datetime = datetime.datetime.utcnow()
#     last_accessed_at: datetime.datetime = datetime.datetime.utcnow()
#     importance: float = 0.0
#     is_shared: bool = False
#     is_reflection: bool = False
#     conversation_id: uuid.UUID
#     clone_id: uuid.UUID


# class MemoryUpdate(BaseModel):
#     memory: str
#     memory_embedding: List[float]
#     last_accessed_at: datetime.datetime
#     importance: float
#     is_shared: bool
#     is_reflection: bool


# class Memory(CommonMixin, MemoryCreate):
#     class Config:
#         orm_mode = True


# class CreatorPartnerProgramSignupBase(BaseModel):
#     name: str
#     email: str
#     phone_number: Optional[str] = None
#     social_media_handles: Optional[str] = None


# class CreatorPartnerProgramSignupCreate(CreatorPartnerProgramSignupBase):
#     pass


# class CreatorPartnerProgramSignupUpdate(CreatorPartnerProgramSignupBase):
#     pass


# class CreatorPartnerProgramSignup(CreatorPartnerProgramSignupBase):
#     id: uuid.UUID
#     user_id: uuid.UUID
#     created_at: datetime.datetime
#     updated_at: datetime.datetime

#     class Config:
#         orm_mode = True


# class NSFWSignupBase(BaseModel):
#     name: str
#     email: str
#     phone_number: Optional[str] = None
#     social_media_handles: Optional[str] = None


# class NSFWSignupCreate(NSFWSignupBase):
#     pass


# class NSFWSignupUpdate(NSFWSignupBase):
#     pass


# class NSFWSignup(NSFWSignupBase):
#     id: uuid.UUID
#     user_id: uuid.UUID
#     created_at: datetime.datetime
#     updated_at: datetime.datetime

#     class Config:
#         orm_mode = True
