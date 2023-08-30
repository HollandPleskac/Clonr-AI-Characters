from __future__ import annotations

import datetime
import enum
import hashlib
import uuid

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
    text_splitter: str | None = None
    max_chunk_size: str | None = None
    chunk_overlap: str | None = None

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


class Monologue(BaseModel):
    id: uuid.UUID = Field(default_factory=uuid.uuid4)
    content: str
    source: str
    embedding: list[float] = Field(default=None, repr=False)
    embedding_model: str | None = Field(default=None, repr=False)
    hash: str = ""

    @validator("hash", always=True)
    def dialogue_hash(cls, v, values) -> str:
        text = values["content"]
        h = hashlib.sha256(text.encode()).hexdigest()
        return h


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


class _MemoryBase(BaseModel):
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
    is_shared: bool = Field(
        default=False,
        detail="Whether this memory is shared across all conversations or not.",
    )
    embedding: list[float] | None = Field(default=None, repr=False)
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

    @property
    def time_str(self) -> str:
        # return DateFormat.relative(self.timestamp, n_largest_times=2)
        return DateFormat.human_readable(self.timestamp)


class Memory(_MemoryBase):
    importance: int = Field(
        detail="The LLM rated importance of this memory. scaled 0-9 to make guidance easier",
        ge=0,
        le=9,
    )


class MemoryWithoutRating(_MemoryBase):
    importance: int | None = Field(
        default=None,
        detail="The LLM rated importance of this memory. scaled 0-9 to make guidance easier",
        ge=0,
        le=9,
    )


class Message(BaseModel):
    id: uuid.UUID = Field(default_factory=uuid.uuid4)
    sender_name: str
    content: str
    timestamp: datetime.datetime = Field(default_factory=get_current_datetime)
    is_clone: bool
    parent_id: uuid.UUID | None = Field(detail="ID of the parent message")

    def to_str(self) -> str:
        # NOTE (Jonny): in the pydantic schema, we do not allow sending <| or |>
        # so that this remains somewhat unhackable.
        name = self.sender_name.capitalize()
        # should be safe since the tags are <|im_start|>assistant etc.
        # and this has a colon at the end.
        return f"[{self.time_str}] <|{name}|>: {self.content}"

    @property
    def time_str(self) -> str:
        # return DateFormat.relative(self.timestamp, n_largest_times=2)
        return DateFormat.human_readable(self.timestamp)
