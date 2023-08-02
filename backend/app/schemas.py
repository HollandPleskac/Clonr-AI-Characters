import datetime
import re
import uuid
from typing import Dict, List, Optional

from fastapi_users.schemas import BaseUser, BaseUserCreate, BaseUserUpdate
from pgvector.sqlalchemy import Vector
from pydantic import BaseModel, Field, validator

from clonr.index import IndexType


class UserRead(BaseUser[uuid.UUID]):
    pass


class UserCreate(BaseUserCreate):
    pass


class UserUpdate(BaseUserUpdate):
    pass


class CommonMixin(BaseModel):
    id: uuid.UUID
    created_at: datetime.datetime
    updated_at: datetime.datetime


class CreatorCreate(BaseModel):
    username: str = Field(
        description="username must be 3 <= len(name) <= 20 characters, start with a letter and only contain hyphens and underscores",
        regex=r"^[a-zA-Z][a-zA-Z0-9_\-]{2,29}$",
    )
    is_public: bool = False


class CreatorPatch(CreatorCreate):
    username: str | None = Field(
        default=None,
        regex=r"^[a-zA-Z][a-zA-Z0-9_]{2,29}$",
    )
    is_active: bool | None = None


class Creator(CreatorCreate):
    user_id: uuid.UUID
    is_active: bool
    is_public: bool
    created_at: datetime.datetime
    updated_at: datetime.datetime

    class Config:
        orm_mode = True


class CloneCreate(BaseModel):
    name: str
    short_description: str
    long_description: str | None = None
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
    creator_id: uuid.UUID
    num_messages: int
    num_conversations: int

    class Config:
        orm_mode = True


class CloneSearchResult(CommonMixin, BaseModel):
    creator_id: uuid.UUID
    name: str
    short_description: str
    avatar_uri: str | None = (
        None  # TODO (Jonny) make sure we don't throw errors here and un None it
    )

    class Config:
        orm_mode = True


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
        regex=r"[a-zA-Z0-9_\-]+",
        description="One word tag describing the source. Letters, numbers, underscores, and hyphens allowed.",
    )
    url: str | None = Field(
        max_length=256, description="The resource URL if applicable", default=None
    )
    index_type: IndexType = Field(
        default=IndexType.list, description="The type of index to build."
    )


# we don't allow updates on the other fields. URL, content, and type are packaged together
# and it'd be too complicated to allow updating these. It's better to just create a new doc
class DocumentUpdate(BaseModel):
    name: str | None = None
    description: str | None = None
    type: str | None = None


class Document(CommonMixin, DocumentCreate):
    clone_id: uuid.UUID

    class Config:
        orm_mode = True


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
    clone_id: uuid.UUID

    class Config:
        orm_mode = True


class TagCreate(BaseModel):
    name: str


class Tag(TagCreate):
    class Config:
        orm_mode = True


# ------------------------------------#


class APIKeyCreate(BaseModel):
    user_id: uuid.UUID
    clone_id: uuid.UUID
    name: Optional[str] = None
    user_id: Optional[uuid.UUID] = None


class APIKey(CommonMixin, APIKeyCreate):
    name: str

    class Config:
        orm_mode = True


class APIKeyOnce(APIKey):
    key: str


class MessageCreate(BaseModel):
    content: str
    sender_name: str


class Message(CommonMixin, MessageCreate):
    from_clone: bool
    conversation_id: uuid.UUID

    class Config:
        orm_mode = True


class ConversationCreate(BaseModel):
    clone_id: uuid.UUID
    user_id: uuid.UUID = None
    name: Optional[str] = None


class Conversation(CommonMixin, ConversationCreate):
    ## This raises an error when fastapi tries to convert
    ## sqlalchemy.exc.MissingGreenlet: greenlet_spawn has not been called
    # messages: Optional[list[Message]] = None

    class Config:
        orm_mode = True


class DocumentCreate(BaseModel):
    content: str
    content_embedding: List[float]
    num_tokens: int
    summary: str
    summary_embedding: List[float]
    is_shared: bool = True


class DocumentUpdate(DocumentCreate):
    pass


class Document(CommonMixin, DocumentCreate):
    clone_id: uuid.UUID

    class Config:
        orm_mode = True


class ExampleDialogueCreate(BaseModel):
    content: str
    content_embedding: List[float]
    num_tokens: int
    summary: str
    summary_embedding: List[float]
    chunk_index: int
    is_shared: bool = True
    conversation_id: uuid.UUID


class ExampleDialogueUpdate(ExampleDialogueCreate):
    pass


class ExampleDialogue(ExampleDialogueCreate):
    class Config:
        orm_mode = True


class MemoryCreate(BaseModel):
    memory: str
    memory_embedding: List[float]
    timestamp: datetime.datetime = datetime.datetime.utcnow()
    last_accessed_at: datetime.datetime = datetime.datetime.utcnow()
    importance: float = 0.0
    is_shared: bool = False
    is_reflection: bool = False
    conversation_id: uuid.UUID
    clone_id: uuid.UUID


class MemoryUpdate(BaseModel):
    memory: str
    memory_embedding: List[float]
    last_accessed_at: datetime.datetime
    importance: float
    is_shared: bool
    is_reflection: bool


class Memory(CommonMixin, MemoryCreate):
    class Config:
        orm_mode = True
