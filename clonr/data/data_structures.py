from __future__ import annotations

import uuid

from pydantic import BaseModel, Field, validator


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
    document_id: uuid.UUID
    embedding: list[float] | None = Field(default=None, repr=False)
    embedding_model: str | None = Field(default=None, repr=False)

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
    embedding: list[float] | None = Field(default=None, repr=False)
    embedding_model: str | None = Field(default=None, repr=False)
    dialogue_id: uuid.UUID


class Dialogue(BaseModel):
    id: uuid.UUID = Field(default_factory=uuid.uuid4)
    character: str = Field(
        detail="The character name. It should also probably be tied to the clone_id, but whatever."
    )
    source: str = Field(
        detail="The input source for this dialogue. Can be manual, discord, text, whatsapp, messenger, etc."
    )
    embedding: list[float] | None = Field(default=None, repr=False)
    embedding_model: str | None = Field(default=None, repr=False)
    message_ids: list[uuid.UUID] = Field(default_factory=lambda: [], repr=False)
