from __future__ import annotations

import datetime
import enum
import hashlib
import uuid
from zoneinfo import ZoneInfo

import randomname
from pydantic import BaseModel, Field, validator

from clonr.utils import get_current_datetime
from clonr.utils.formatting import DateFormat


class IndexType(str, enum.Enum):
    list: str = "list"
    list_with_context: str = "list_with_context"
    tree: str = "tree"
    tree_with_context: str = "tree_with_context"


class Document(BaseModel):
    id: uuid.UUID = Field(default_factory=uuid.uuid4)
    content: str = Field(repr=False)
    name: str = Field(default_factory=randomname.get_name)
    description: str | None = None
    # wikipedia, personal site, pdf?
    type: str | None = None  # wiki, messages, website, google search, etc.
    url: str | None = None
    index_type: IndexType | None = None
    embedding: list[float] = Field(default=None, repr=False)
    embedding_model: str | None = Field(default=None, repr=False)
    hash: str = ""

    @validator("hash", always=True)
    def doc_hash(cls, v, values) -> str:
        text = values["content"]
        h = hashlib.sha256(text.encode()).hexdigest()
        return h

    def __eq__(self, other):
        return self.hash == other.hash

    def __repr__(self):
        name = self.__class__.__name__
        content = self.content
        msg = f"... + {len(content) - 30} chars"
        if len(content) > 30 + len(msg):
            content = content[:30] + msg
        return f"{name}(id={str(self.id)}, content={content})"


class Chunk(BaseModel):
    id: uuid.UUID = Field(default_factory=uuid.uuid4)
    content: str
    index: int
    context: str | None = None
    embedding: list[float] = Field(default=None, repr=False)
    embedding_model: str | None = Field(default=None, repr=False)
    document_id: uuid.UUID

    def __eq__(self, other):
        return (
            issubclass(other, Chunk) or isinstance(other, Chunk)
        ) and self.id == other.id

    def __repr__(self):
        name = self.__class__.__name__
        content = self.content
        msg = f"... + {len(content) - 30} chars"
        if len(content) > 30 + len(msg):
            content = content[:30] + msg
        return f"{name}(index={self.index}, content={content})"


class Node(Chunk):
    # previous_id: uuid.UUID | None = None
    # next_id: uuid.UUID | None = None
    is_leaf: bool
    depth: int
    parent_id: uuid.UUID | None = None
    child_ids: list[uuid.UUID] | None = None

    def __repr__(self):
        name = self.__class__.__name__
        content = self.content
        msg = f"... + {len(content) - 30} chars"
        if len(content) > 30 + len(msg):
            content = content[:30] + msg
        return f"{name}(index={self.index}, content={content})"


class DialogueMessage(BaseModel):
    id: uuid.UUID = Field(default_factory=uuid.uuid4)
    sender_name: str
    content: str
    index: int
    is_clone: bool
    dialogue_id: uuid.UUID
    embedding: list[float] = Field(default=None, repr=False)
    embedding_model: str | None = Field(default=None, repr=False)
    hash: str = ""

    @validator("hash", always=True)
    def dialogue_hash(cls, v, values) -> str:
        text = values["content"]
        h = hashlib.sha256(text.encode()).hexdigest()
        return h


class Dialogue(BaseModel):
    id: uuid.UUID = Field(default_factory=uuid.uuid4)
    source: str = Field(
        detail="The input source for this dialogue. Can be manual, discord, text, whatsapp, messenger, etc."
    )
    message_ids: list[uuid.UUID] = Field(default_factory=lambda: [], repr=False)
    messages: list[DialogueMessage] = Field(default_factory=lambda: [], repr=False)
    embedding: list[float] = Field(default=None, repr=False)
    embedding_model: str | None = Field(default=None, repr=False)

    @classmethod
    def _msgs_to_str(cls, messages: list[DialogueMessage]):
        return "\n".join(f"{x.sender_name.capitalize()}: {x.content}" for x in messages)

    @property
    def content(self):
        return self._msgs_to_str(self.messages)

    def to_str(self):
        return self.content


class Memory(BaseModel):
    id: uuid.UUID = Field(default_factory=uuid.uuid4)
    content: str
    timestamp: datetime.datetime = Field(
        detail="The time at which the memory occurs, which may be different than the time it was created at. "
        "This can happen when uploading past events. Stored as UTC. Converted to local time as necessary",
        default_factory=get_current_datetime,
    )
    last_accessed_at: datetime.datetime = Field(
        detail="date of last access in the DB. This counts reflections and message retrieval?",
        default_factory=get_current_datetime,
    )
    importance: int = Field(
        detail="The LLM rated importance of this memory. scaled 0-9 to make guidance easier",
        ge=0,
        le=9,
    )
    embedding: list[float] = Field(default=None, repr=False)
    embedding_model: str | None = Field(default=None, repr=False)
    depth: int = Field(
        default=0, detail="What depth of reflection this is. New memories are depth 0."
    )
    parent_ids: list[uuid.UUID] = Field(
        default_factory=lambda: [],
        detail="Higher-order reflections that this memory is apart of",
    )
    child_ids: list[uuid.UUID] = Field(
        default_factory=lambda: [],
        detail="lower-order memories used to produce this reflection",
    )

    def to_str(self) -> str:
        dt_str = DateFormat.human_readable(self.timestamp)
        return f"[{dt_str}] {self.content}"

    # TODO (Jonny): Need a way to prevent this from returning messages
    # that are already displayed. Mostly an issue early in the conversation.


class Message(BaseModel):
    id: uuid.UUID = Field(default_factory=uuid.uuid4)
    sender_name: str
    content: str
    timestamp: datetime.datetime = Field(default_factory=get_current_datetime)
    is_clone: bool

    def to_str(self) -> str:
        dt_str = DateFormat.human_readable(self.timestamp)
        name = "me" if self.is_clone else self.speaker
        name = name.capitalize()
        return f"[{dt_str}] {name}: {self.content}"
