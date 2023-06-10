import datetime
import uuid

import randomname
from fastapi_users.db import (
    SQLAlchemyBaseOAuthAccountTableUUID,
    SQLAlchemyBaseUserTableUUID,
)
import sqlalchemy as sa
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, relationship
from pgvector.sqlalchemy import Vector
from typing import Optional, List, Dict, Any


class Base(DeclarativeBase):
    type_annotation_map = {List[float]: Vector, dict[str, Any]: JSON}

    pass


class OAuthAccount(SQLAlchemyBaseOAuthAccountTableUUID, Base):
    user_id: Mapped[uuid.UUID] = mapped_column(
        sa.ForeignKey("users.id", ondelete="cascade"), nullable=False
    )


class User(Base, SQLAlchemyBaseUserTableUUID):
    __tablename__ = "users"
    oauth_accounts: Mapped[list[OAuthAccount]] = relationship(
        "OAuthAccount", lazy="joined"
    )
    clones: Mapped[list["Clone"]] = relationship("Clone", lazy="select")

    def __repr__(self):
        return f"User(id={self.id}, oauth_accounts={self.oauth_accounts}, clones={self.clones})"


class CommonMixin:
    id: Mapped[uuid.UUID] = mapped_column(
        primary_key=True, server_default=sa.text("gen_random_uuid()")
    )
    created_at: Mapped[datetime.datetime] = mapped_column(
        sa.DateTime(timezone=True), server_default=sa.func.now()
    )
    updated_at: Mapped[datetime.datetime] = mapped_column(
        sa.DateTime(timezone=True),
        server_default=sa.func.now(),
        onupdate=sa.func.current_timestamp(),
    )


class Clone(CommonMixin, Base):
    __tablename__ = "clones"

    name: Mapped[str]
    description: Mapped[str]
    motivation: Mapped[str]
    greeting_message: Mapped[str]
    is_active: Mapped[bool] = mapped_column(default=True)
    is_public: Mapped[bool] = mapped_column(default=False)
    user_id: Mapped[uuid.UUID] = mapped_column(
        sa.ForeignKey("users.id", ondelete="cascade"), nullable=False
    )
    user: Mapped["User"] = relationship("User", back_populates="clones")
    conversations: Mapped[list["Conversation"]] = relationship(
        "Conversation", lazy="select"
    )
    documents: Mapped[list["Document"]] = relationship("Document", lazy="select")
    api_keys: Mapped[list["APIKey"]] = relationship("APIKey", lazy="select")

    def __repr__(self):
        return f"Clone(clone_id={self.id}, active={self.is_active}, public={self.is_public})"


class APIKey(CommonMixin, Base):
    __tablename__ = "api_keys"

    hashed_key: Mapped[str] = mapped_column(unique=True)
    name: Mapped[str] = mapped_column(default=randomname.get_name)
    clone_id: Mapped[uuid.UUID] = mapped_column(
        sa.ForeignKey("clones.id", ondelete="cascade"), nullable=False
    )
    clone: Mapped["Clone"] = relationship(
        "Clone", back_populates="api_keys", lazy="joined"
    )

    def __repr__(self):
        return f"APIKey(hashed_key={self.hashed_key}, clone_id={self.clone_id})"


class Conversation(CommonMixin, Base):
    __tablename__ = "conversations"

    name: Mapped[str] = mapped_column(default=randomname.get_name)
    messages: Mapped[list["Message"]] = relationship("Message", lazy="select")
    clone_id: Mapped[uuid.UUID] = mapped_column(
        ForeignKey("clones.id", ondelete="cascade"), nullable=False
    )
    clone: Mapped["Clone"] = relationship("Clone", back_populates="conversations")
    example_dialogues: Mapped[list["ExampleDialogue"]] = relationship(
        "ExampleDialogue", lazy="select"
    )
    memories: Mapped[list["Memory"]] = relationship("Memory", lazy="select")

    def __repr__(self):
        return f"Conversation(name={self.name}, clone_id={self.clone_id})"


class Message(CommonMixin, Base):
    __tablename__ = "messages"

    content: Mapped[str]
    sender_name: Mapped[str]
    from_clone: Mapped[bool] = mapped_column(default=False)
    conversation_id: Mapped[uuid.UUID] = mapped_column(
        sa.ForeignKey("conversations.id", ondelete="cascade"), nullable=False
    )
    conversation: Mapped["Conversation"] = relationship(
        "Conversation", back_populates="messages"
    )

    def __repr__(self):
        return f"Message(content={self.content}, sender={self.sender}, from_clone={self.from_clone})"


class Document(CommonMixin, Base):
    __tablename__ = "documents"

    content: Mapped[str]
    summary: Mapped[str]
    chunk_index: Mapped[int]
    content_embedding: Mapped[List[float]]
    summary_embedding: Mapped[List[float]]
    is_shared: Mapped[bool] = mapped_column(default=True)

    clone_id: Mapped[uuid.UUID] = mapped_column(
        sa.ForeignKey("clones.id", ondelete="cascade"), nullable=False
    )
    clone: Mapped["Clone"] = relationship("Clone", back_populates="documents")

    def __repr__(self):
        return f"Fact(fact={self.fact})"

    def split(self):
        pass


class Document(CommonMixin, Base):
    __tablename__ = "documents"

    chunks: Mapped[list["Chunk"]] = relationship("Chunk", back_populates="document")
    clone_id: Mapped[uuid.UUID] = mapped_column(
        sa.ForeignKey("clones.id", ondelete="cascade"), nullable=False
    )
    clone: Mapped["Clone"] = relationship("Clone", back_populates="documents")


class ExampleDialogue(CommonMixin, Base):
    __tablename__ = "example_dialogues"

    content: Mapped[str]
    content_embedding: Mapped[List[float]]
    num_tokens: Mapped[int]
    summary: Mapped[str]
    summary_embedding: Mapped[List[float]]
    chunk_index: Mapped[int]
    is_shared: Mapped[bool] = mapped_column(default=True)
    conversation_id: Mapped[uuid.UUID] = mapped_column(
        sa.ForeignKey("conversations.id", ondelete="cascade"), nullable=False
    )
    clone: Mapped["Conversation"] = relationship(
        "Conversation", back_populates="example_dialogues"
    )

    def __repr__(self):
        return f"ExampleDialogue(example_dialogue={self.example_dialogue})"

    def split(self):
        pass


memory_to_memory = sa.Table(
    "memory_to_memory",
    Base.metadata,
    sa.Column("parent_id", uuid.UUID, sa.ForeignKey("memories.id"), primary_key=True),
    sa.Column("child_id", uuid.UUID, sa.ForeignKey("memories.id"), primary_key=True),
)


class Memory(CommonMixin, Base):
    __tablename__ = "memories"

    memory: Mapped[str]
    memory_embedding: Mapped[List[float]]
    importance: Mapped[float]
    timestamp: Mapped[datetime.datetime] = mapped_column(
        sa.DateTime(timezone=True),
        server_default=sa.func.now(),
    )
    last_accessed_at: Mapped[datetime.datetime] = mapped_column(
        sa.DateTime(timezone=True),
        server_default=sa.func.now(),
    )
    is_shared: Mapped[bool] = mapped_column(default=False)
    is_reflection: Mapped[bool]
    reflection_memories: Mapped[list["Memory"]] = relationship(
        "Node",
        secondary=memory_to_memory,
        primaryjoin=id == memory_to_memory.c.left_node_id,
        secondaryjoin=id == memory_to_memory.c.right_node_id,
        backref="left_nodes",
    )

    conversation_id: Mapped[Optional[uuid.UUID]] = mapped_column(
        sa.ForeignKey("conversations.id", ondelete="cascade")
    )
    clone_id: Mapped[uuid.UUID] = mapped_column(
        sa.ForeignKey("clones.id", ondelete="cascade")
    )

    def __repr__(self):
        if self.is_reflection:
            return f"Reflection(timestamp={self.timestamp}, memory={self.memory})"
        return f"Memory(timestamp={self.timestamp}, memory={self.memory})"


# class DocumentCollection(CommonMixin, Base):
#     __tablename__ = "document_collections"

#     name: Mapped[str] = mapped_column(nullable=False)
#     user_id: Mapped[uuid.UUID] = mapped_column(
#         ForeignKey("users.id", ondelete="cascade"), nullable=False
#     )
#     clone_id: Mapped[uuid.UUID] = mapped_column(
#         ForeignKey("clones.id", ondelete="cascade"), nullable=False
#     )
#     vector_db: Mapped[str] = mapped_column(nullable=False)

#     user: Mapped["User"] = relationship("User", back_populates="document_collections")
#     clone: Mapped["Clone"] = relationship(
#         "Clone", back_populates="document_collections"
#     )
#     documents: Mapped[list["Document"]] = relationship(
#         "Document", back_populates="document_collections"
#     )


# class Document(CommonMixin, Base):
#     __tablename__ = "document"

#     url: Mapped[str] = mapped_column(nullable=False)
#     document_metadata: Mapped[str] = mapped_column(nullable=False)
#     document_collection: Mapped["DocumentCollection"] = relationship(
#         "DocumentCollection", back_populates="documents"
#     )


# __all__ = [
#     "Base",
#     "Clone",
#     "User",
#     "Conversation",
#     "Message",
#     "Document",
#     "DocumentCollection",
# ]
