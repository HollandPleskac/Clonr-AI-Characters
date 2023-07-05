from __future__ import annotations

import datetime
import uuid
from zoneinfo import ZoneInfo

from pydantic import BaseModel, Field, validator

from clonr.utils import get_current_datetime
from clonr.utils.formatting import datediff_to_str


class Document(BaseModel):
    id: uuid.UUID = Field(default_factory=uuid.uuid4)
    content: str = Field(repr=False)
    embedding: list[float] = Field(default=None, repr=False)
    embedding_model: str | None = Field(default=None, repr=False)

    def __eq__(self, other):
        return self.id == other.id

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
    speaker: str
    content: str
    index: int
    is_character: bool
    dialogue_id: uuid.UUID
    embedding: list[float] = Field(default=None, repr=False)
    embedding_model: str | None = Field(default=None, repr=False)


class Dialogue(BaseModel):
    id: uuid.UUID = Field(default_factory=uuid.uuid4)
    character: str = Field(
        detail="The character name. It should also probably be tied to the clone_id, but whatever."
    )
    source: str = Field(
        detail="The input source for this dialogue. Can be manual, discord, text, whatsapp, messenger, etc."
    )
    message_ids: list[uuid.UUID] = Field(default_factory=lambda: [], repr=False)
    messages: list[DialogueMessage] = Field(default_factory=lambda: [], repr=False)
    embedding: list[float] = Field(default=None, repr=False)
    embedding_model: str | None = Field(default=None, repr=False)

    @property
    def content(self):
        return "\n".join(f"<{x.speaker}>: {x.content}" for x in self.messages)


class Memory(BaseModel):
    id: uuid.UUID = Field(default_factory=uuid.uuid4)
    content: str
    timestamp: datetime.datetime = Field(
        detail="The time at which the memory occurs, which may be different than the time it was created at. Stored as UTC. Converted to local time as necessary",
        default_factory=get_current_datetime,
    )
    importance: int = Field(
        detail="The LLM rated importance of this memory. scaled 0-9 to make guidance easier",
        ge=0,
        le=9,
    )
    embedding: list[float] = Field(default=None, repr=False)
    embedding_model: str | None = Field(default=None, repr=False)

    def to_relative_dt_str(self, tz: ZoneInfo | None = None):
        now = get_current_datetime(tz=tz)
        dt_str = datediff_to_str(start_date=self.timestamp, end_date=now)
        return f"[{dt_str}] {self.content}"

    def to_str(self, tz: ZoneInfo | None = None):
        dt = self.timestamp
        if tz is not None:
            dt = dt.astimezone(tz=ZoneInfo(tz))
        dt_str = dt.strftime("%Y-%m-%d %H:%M:%S")
        return f"[{dt_str}] {self.content}"


class Message(BaseModel):
    id: uuid.UUID = Field(default_factory=uuid.uuid4)
    speaker: str
    content: str
    timestamp: datetime
    is_character: bool
