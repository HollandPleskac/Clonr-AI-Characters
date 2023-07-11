import datetime
import uuid
from typing import Any, Dict, List, Optional

import randomname
import sqlalchemy as sa
from fastapi_users.db import (
    SQLAlchemyBaseOAuthAccountTableUUID,
    SQLAlchemyBaseUserTableUUID,
)
from pgvector.sqlalchemy import Vector
from sqlalchemy.dialects.postgresql import JSON
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, relationship


class Base(DeclarativeBase):
    type_annotation_map = {List[float]: Vector, dict[str, Any]: JSON}


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


class OAuthAccount(SQLAlchemyBaseOAuthAccountTableUUID, Base):
    user_id: Mapped[uuid.UUID] = mapped_column(
        sa.ForeignKey("users.id", ondelete="cascade"), nullable=False
    )


class User(Base, SQLAlchemyBaseUserTableUUID):
    """Contains the fields:
    id, email, hashed_password, is_active, is_superuser, is_verified
    """

    __tablename__ = "users"
    created_at: Mapped[datetime.datetime] = mapped_column(
        sa.DateTime(timezone=True), server_default=sa.func.now()
    )
    updated_at: Mapped[datetime.datetime] = mapped_column(
        sa.DateTime(timezone=True),
        server_default=sa.func.now(),
        onupdate=sa.func.current_timestamp(),
    )
    # (Jonny): Idk why, but select breaks with greenlet spawn error and this doesn't
    oauth_accounts: Mapped[list[OAuthAccount]] = relationship(
        "OAuthAccount", lazy="joined"
    )
    # (Jonny): probably never a situation where you don't need clones when grabbing a user.
    clones: Mapped[list["Clone"]] = relationship(
        "Clone", back_populates="user", lazy="joined"
    )

    def __repr__(self):
        return f"User(id={self.id})"


class APIKey(CommonMixin, Base):
    __tablename__ = "api_keys"

    hashed_key: Mapped[str] = mapped_column(unique=True)
    name: Mapped[str] = mapped_column(default=randomname.get_name)
    clone_id: Mapped[uuid.UUID] = mapped_column(
        sa.ForeignKey("clones.id", ondelete="cascade"), nullable=False
    )
    clone: Mapped["Clone"] = relationship("Clone", back_populates="api_keys")

    def __repr__(self):
        return f"APIKey(hashed_key={self.hashed_key}, clone_id={self.clone_id})"


class Clone(CommonMixin, Base):
    __tablename__ = "clones"

    name: Mapped[str]
    short_description: Mapped[str]
    long_description: Mapped[str]
    greeting_message: Mapped[str]
    is_active: Mapped[bool] = mapped_column(default=True)
    is_public: Mapped[bool] = mapped_column(default=False)
    user_id: Mapped[uuid.UUID] = mapped_column(
        sa.ForeignKey("users.id", ondelete="cascade"), nullable=False
    )
    # (Jonny): lazy="select" is important here. We cache the clone model so we don't want this loading
    # and creating a vulnerability where user info is stored in the cache.
    user: Mapped["User"] = relationship("User", back_populates="clones", lazy="select")
    api_keys: Mapped[list["APIKey"]] = relationship("APIKey", back_populates="clone")
    conversations: Mapped[list["Conversation"]] = relationship(
        "Conversation", back_populates="clone"
    )
    messages: Mapped[list["Message"]] = relationship("Message", back_populates="clone")
    documents: Mapped[list["Document"]] = relationship(
        "Document", back_populates="clone"
    )
    nodes: Mapped[list["Node"]] = relationship("Node", back_populates="clone")
    example_dialogues: Mapped[list["ExampleDialogue"]] = relationship(
        "ExampleDialogue", back_populates="clone"
    )
    example_dialogue_messages: Mapped[list["ExampleDialogueMessage"]] = relationship(
        "ExampleDialogueMessage", back_populates="clone"
    )
    memories: Mapped[list["Memory"]] = relationship("Memory", back_populates="clone")
    agent_summaries: Mapped[list["AgentSummary"]] = relationship(
        "AgentSummary", back_populates="clone"
    )
    entity_context_summaries: Mapped[list["EntityContextSummary"]] = relationship(
        "EntityContextSummary", back_populates="clone"
    )

    def __repr__(self):
        return f"Clone(clone_id={self.id}, active={self.is_active}, public={self.is_public})"


class Conversation(CommonMixin, Base):
    __tablename__ = "conversations"

    name: Mapped[str] = mapped_column(
        default=randomname.get_name
    )  # (Jonny) is this necessary?
    clone_id: Mapped[uuid.UUID] = mapped_column(
        sa.ForeignKey("clones.id", ondelete="cascade"), nullable=False
    )
    clone: Mapped["Clone"] = relationship("Clone", back_populates="conversations")
    messages: Mapped[list["Message"]] = relationship(
        "Message", back_populates="conversation"
    )
    memories: Mapped[list["Memory"]] = relationship(
        "Memory", back_populates="conversation"
    )
    agent_summaries: Mapped[list["AgentSummary"]] = relationship(
        "AgentSummary", back_populates="conversation"
    )
    entity_context_summaries: Mapped[list["EntityContextSummary"]] = relationship(
        "EntityContextSummary", back_populates="conversation"
    )

    def __repr__(self):
        return f"Conversation(name={self.name}, clone_id={self.clone_id})"


class Message(CommonMixin, Base):
    __tablename__ = "messages"

    content: Mapped[str]
    sender_name: Mapped[str]
    is_clone: Mapped[bool]
    timestamp: Mapped[datetime.datetime] = mapped_column(
        sa.DateTime(timezone=True), server_default=sa.func.now()
    )
    clone_id: Mapped[uuid.UUID] = mapped_column(
        sa.ForeignKey("clones.id", ondelete="cascade"), nullable=False
    )
    clone: Mapped["Clone"] = relationship("Clone", back_populates="messages")
    conversation_id: Mapped[uuid.UUID] = mapped_column(
        sa.ForeignKey("conversations.id", ondelete="cascade"), nullable=False
    )
    conversation: Mapped["Conversation"] = relationship(
        "Conversation", back_populates="messages"
    )

    def __repr__(self):
        return f"Message(content={self.content}, sender={self.sender_name}, is_clone={self.from_clone})"


import enum


class IndexType(enum.Enum):
    list: str = "list"
    tree: str = "tree"


class Document(CommonMixin, Base):
    __tablename__ = "documents"

    content: Mapped[str]
    hash: Mapped[str] = mapped_column(index=True)
    name: Mapped[str]
    description: Mapped[Optional[str]] = mapped_column(default=None)
    # wiki, messages, website, google search, etc.
    type: Mapped[Optional[str]] = mapped_column(default=None)
    url: Mapped[Optional[str]] = mapped_column(default=None)
    index_type: Mapped[IndexType] = mapped_column(nullable=True)
    embedding: Mapped[List[float]]
    embedding_model: Mapped[str]
    clone_id: Mapped[uuid.UUID] = mapped_column(
        sa.ForeignKey("clones.id", ondelete="cascade"), nullable=False
    )
    clone: Mapped["Clone"] = relationship("Clone", back_populates="documents")
    nodes: Mapped[list["Node"]] = relationship("Node", back_populates="document")

    def __eq__(self, other):
        return self.id == other.id

    def __repr__(self):
        name = self.__class__.__name__
        content = self.content
        msg = f"... + {len(content) - 30} chars"
        if len(content) > 30 + len(msg):
            content = content[:30] + msg
        return f"{name}(id={str(self.id)}, content={content})"


node_to_node = sa.Table(
    "node_to_node",
    Base.metadata,
    sa.Column("parent_id", sa.Uuid, sa.ForeignKey("nodes.id"), primary_key=True),
    sa.Column("child_id", sa.Uuid, sa.ForeignKey("nodes.id"), primary_key=True),
)


class Node(CommonMixin, Base):
    __tablename__ = "nodes"

    index: Mapped[int]
    content: Mapped[str]
    context: Mapped[Optional[str]] = mapped_column(nullable=True)
    embedding: Mapped[List[float]]
    embedding_model: Mapped[str]
    is_leaf: Mapped[bool]  # Note (Jonny): isn't this redundant with depth?
    depth: Mapped[int]
    parent_id: Mapped[uuid.UUID] = mapped_column(
        sa.ForeignKey("nodes.id"), nullable=True
    )
    parent: Mapped["Node"] = relationship(
        "Node", back_populates="children", remote_side="Node.id"
    )
    children: Mapped[list["Node"]] = relationship("Node", back_populates="parent")
    document_id: Mapped[uuid.UUID] = mapped_column(
        sa.ForeignKey("documents.id", ondelete="cascade"), nullable=False
    )
    document: Mapped["Document"] = relationship("Document", back_populates="nodes")
    clone_id: Mapped[uuid.UUID] = mapped_column(
        sa.ForeignKey("clones.id", ondelete="cascade"), nullable=False
    )
    clone: Mapped["Clone"] = relationship("Clone", back_populates="nodes")

    def __eq__(self, other):
        return self.id == other.id

    def __repr__(self):
        name = self.__class__.__name__
        content = self.content
        msg = f"... + {len(content) - 30} chars"
        if len(content) > 30 + len(msg):
            content = content[:30] + msg
        return f"{name}(id={str(self.id)}, index={self.index}, content={content})"


class ExampleDialogue(CommonMixin, Base):
    __tablename__ = "example_dialogues"

    source: Mapped[str]
    messages: Mapped[list["ExampleDialogueMessage"]] = relationship(
        "ExampleDialogueMessage", back_populates="dialogue"
    )
    embedding: Mapped[List[float]]
    embedding_model: Mapped[str]
    clone_id: Mapped[uuid.UUID] = mapped_column(
        sa.ForeignKey("clones.id", ondelete="cascade"), nullable=False
    )
    clone: Mapped["Clone"] = relationship("Clone", back_populates="example_dialogues")

    @property
    def content(self):
        return "\n".join(
            f"<{x.sender_name.capitalize()}>: {x.content}" for x in self.messages
        )

    def __repr__(self):
        return f"ExampleDialogue(id={str(self.id)}, source={self.source})"


class ExampleDialogueMessage(CommonMixin, Base):
    __tablename__ = "example_dialogue_messages"

    index: Mapped[int]
    content: Mapped[str]
    sender_name: Mapped[str]
    is_clone: Mapped[bool]
    embedding: Mapped[List[float]]
    embedding_model: Mapped[str]
    dialogue_id: Mapped[uuid.UUID] = mapped_column(
        sa.ForeignKey("example_dialogues.id", ondelete="cascade")
    )
    dialogue: Mapped["ExampleDialogue"] = relationship(
        "ExampleDialogue", back_populates="messages"
    )
    clone_id: Mapped[uuid.UUID] = mapped_column(
        sa.ForeignKey("clones.id", ondelete="cascade"), nullable=False
    )
    clone: Mapped["Clone"] = relationship(
        "Clone", back_populates="example_dialogue_messages"
    )

    def __repr__(self):
        name = self.__class__.__name__
        content = self.content
        msg = f"... + {len(content) - 30} chars"
        if len(content) > 30 + len(msg):
            content = content[:30] + msg
        return f"{name}(sender_name={self.sender_name}, is_clone={self.is_clone}, content={content})"


memory_to_memory = sa.Table(
    "memory_to_memory",
    Base.metadata,
    sa.Column("parent_id", sa.Uuid, sa.ForeignKey("memories.id"), primary_key=True),
    sa.Column("child_id", sa.Uuid, sa.ForeignKey("memories.id"), primary_key=True),
)


# Taken from: https://docs.sqlalchemy.org/en/20/orm/join_conditions.html#self-referential-many-to-many
class Memory(CommonMixin, Base):
    __tablename__ = "memories"

    content: Mapped[str]
    embedding: Mapped[List[float]]
    embedding_model: Mapped[str]
    timestamp: Mapped[datetime.datetime] = mapped_column(sa.DateTime(timezone=True))
    last_accessed_at: Mapped[datetime.datetime] = mapped_column(
        sa.DateTime(timezone=True)
    )
    importance: Mapped[int]
    is_shared: Mapped[bool] = mapped_column(default=False)
    depth: Mapped[int] = mapped_column(default=0)
    children: Mapped[list["Memory"]] = relationship(
        "Memory",
        secondary=memory_to_memory,
        primaryjoin="Memory.id == memory_to_memory.c.parent_id",
        secondaryjoin="Memory.id == memory_to_memory.c.child_id",
        backref="parents",
    )
    conversation_id: Mapped[Optional[uuid.UUID]] = mapped_column(
        sa.ForeignKey("conversations.id", ondelete="cascade")
    )
    conversation: Mapped["Conversation"] = relationship(
        "Conversation", back_populates="memories"
    )
    clone_id: Mapped[uuid.UUID] = mapped_column(
        sa.ForeignKey("clones.id", ondelete="cascade")
    )
    clone: Mapped["Clone"] = relationship("Clone", back_populates="memories")

    def __repr__(self):
        name = "Memory" if self.depth <= 0 else "Reflection"
        return (
            f"{name}(depth={self.depth}, timestamp={self.timestamp}, "
            f"importance={self.importance}, content={self.content}))"
        )


class AgentSummary(CommonMixin, Base):
    __tablename__ = "agent_summaries"

    content: Mapped[str]
    timestamp: Mapped[datetime.datetime] = mapped_column(sa.DateTime(timezone=True))
    conversation_id: Mapped[Optional[uuid.UUID]] = mapped_column(
        sa.ForeignKey("conversations.id", ondelete="cascade")
    )
    conversation: Mapped["Conversation"] = relationship(
        "Conversation", back_populates="agent_summaries"
    )
    clone_id: Mapped[uuid.UUID] = mapped_column(
        sa.ForeignKey("clones.id", ondelete="cascade")
    )
    clone: Mapped["Clone"] = relationship("Clone", back_populates="agent_summaries")

    def __repr__(self):
        name = self.__class__.__name__
        content = self.content
        msg = f"... + {len(content) - 30} chars"
        if len(content) > 30 + len(msg):
            content = content[:30] + msg
        return f"{name}(id={str(self.id)}, content={content})"


class EntityContextSummary(CommonMixin, Base):
    __tablename__ = "entity_context_summaries"

    content: Mapped[str]
    entity_name: Mapped[str]
    timestamp: Mapped[datetime.datetime] = mapped_column(sa.DateTime(timezone=True))
    conversation_id: Mapped[Optional[uuid.UUID]] = mapped_column(
        sa.ForeignKey("conversations.id", ondelete="cascade")
    )
    conversation: Mapped["Conversation"] = relationship(
        "Conversation", back_populates="entity_context_summaries"
    )
    clone_id: Mapped[uuid.UUID] = mapped_column(
        sa.ForeignKey("clones.id", ondelete="cascade")
    )
    clone: Mapped["Clone"] = relationship(
        "Clone", back_populates="entity_context_summaries"
    )

    def __repr__(self):
        name = self.__class__.__name__
        content = self.content
        msg = f"... + {len(content) - 30} chars"
        if len(content) > 30 + len(msg):
            content = content[:30] + msg
        return f"{name}(id={str(self.id)}, entity_name={self.entity_name}, content={content})"
