import datetime
import enum
import uuid
from typing import Any, Optional

import randomname
import sqlalchemy as sa
from fastapi_users.db import (
    SQLAlchemyBaseOAuthAccountTableUUID,
    SQLAlchemyBaseUserTableUUID,
)
from pgvector.sqlalchemy import Vector
from sqlalchemy.dialects.postgresql import JSON
from sqlalchemy.ext.hybrid import Comparator, hybrid_property
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, relationship


class CaseInsensitiveComparator(Comparator[str]):
    # taken from https://docs.sqlalchemy.org/en/20/orm/extensions/hybrid.html#building-custom-comparators
    def __eq__(self, other: Any) -> sa.ColumnElement[bool]:  # type: ignore[override]  # noqa: E501
        return sa.func.lower(self.__clause_element__()) == sa.func.lower(other)

    def ilike(self, other: Any, **kwargs) -> sa.ColumnElement[bool]:
        return sa.func.lower(self.__clause_element__()).ilike(other.lower(), **kwargs)

    def like(self, other: Any, **kwargs) -> sa.ColumnElement[bool]:
        return sa.func.lower(self.__clause_element__()).like(other.lower(), **kwargs)

    # (Jonny): dunno if this works
    def levenshtein(self, other: Any, **kwargs) -> sa.ColumnElement[int]:
        return sa.func.levenshtein(
            sa.func.lower(self.__clause_element__()), other.lower()
        )


class Base(DeclarativeBase):
    type_annotation_map = {list[float]: Vector, dict[str, Any]: JSON}


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


# Each created clone can have many users talking to it
# And each user can talk to many clones
users_to_clones = sa.Table(
    "users_to_clones",
    Base.metadata,
    sa.Column("user_id", sa.ForeignKey("users.id"), primary_key=True),
    sa.Column("clone_id", sa.ForeignKey("clones.id"), primary_key=True),
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
    private_chat_name: Mapped[str] = mapped_column(default="user")
    is_banned: Mapped[bool] = mapped_column(default=False)
    # (Jonny): Idk why, but select breaks with greenlet spawn error and this doesn't
    oauth_accounts: Mapped[list[OAuthAccount]] = relationship(
        "OAuthAccount", lazy="joined"
    )
    # (Jonny): probably never a situation where you don't need clones when grabbing a user.
    clones: Mapped[list["Clone"]] = relationship(
        secondary=users_to_clones, back_populates="users"
    )
    creator: Mapped["Creator"] = relationship("Creator", back_populates="user")
    llm_calls: Mapped[list["LLMCall"]] = relationship(
        "LLMCall", back_populates="user", passive_deletes=True
    )
    # Whether user is subscribed to premium plan, i.e. is paid 
    is_subscribed: Mapped[bool] = mapped_column(default=False)

    # Number of free msgs sent
    num_free_messages_sent: Mapped[int] = mapped_column(default=0)

    def __repr__(self):
        return f"User(id={self.id})"


class Creator(Base):
    __tablename__ = "creators"

    username: Mapped[str] = mapped_column(unique=True)
    user_id: Mapped[uuid.UUID] = mapped_column(
        sa.ForeignKey("users.id", ondelete="cascade"), nullable=False, primary_key=True
    )
    created_at: Mapped[datetime.datetime] = mapped_column(
        sa.DateTime(timezone=True), server_default=sa.func.now()
    )
    updated_at: Mapped[datetime.datetime] = mapped_column(
        sa.DateTime(timezone=True),
        server_default=sa.func.now(),
        onupdate=sa.func.current_timestamp(),
    )
    is_active: Mapped[bool] = mapped_column(default=True)
    is_public: Mapped[bool] = mapped_column(default=False)
    user: Mapped["User"] = relationship("User", back_populates="creator")
    clones: Mapped[list["Clone"]] = relationship("Clone", back_populates="creator")


# class APIKey(CommonMixin, Base):
#     __tablename__ = "api_keys"

#     hashed_key: Mapped[str] = mapped_column(unique=True)
#     name: Mapped[str] = mapped_column(default=randomname.get_name)
#     user_id: Mapped[uuid.UUID] = mapped_column(
#         sa.ForeignKey("users.id", ondelete="cascade"), nullable=False
#     )
#     clone_id: Mapped[uuid.UUID] = mapped_column(
#         sa.ForeignKey("clones.id", ondelete="cascade"), nullable=False
#     )
#     clone: Mapped["Clone"] = relationship("Clone", back_populates="api_keys")

#     def __repr__(self):
#         return f"APIKey(hashed_key={self.hashed_key}, clone_id={self.clone_id})"


clones_to_tags = sa.Table(
    "clones_to_tags",
    Base.metadata,
    sa.Column("tag", sa.Text, sa.ForeignKey("tags.name"), primary_key=True),
    sa.Column("clone_id", sa.Uuid, sa.ForeignKey("clones.id"), primary_key=True),
)


class Tag(Base):
    __tablename__ = "tags"

    name: Mapped[str] = mapped_column(primary_key=True, unique=True)
    created_at: Mapped[datetime.datetime] = mapped_column(
        sa.DateTime(timezone=True), server_default=sa.func.now()
    )
    updated_at: Mapped[datetime.datetime] = mapped_column(
        sa.DateTime(timezone=True),
        server_default=sa.func.now(),
        onupdate=sa.func.current_timestamp(),
    )
    clones: Mapped[list["Clone"]] = relationship(
        secondary=clones_to_tags, back_populates="tags"
    )


class Clone(CommonMixin, Base):
    __tablename__ = "clones"

    name: Mapped[str]
    short_description: Mapped[str]
    # TODO (Jonny): make a separate Image table for when Creators have multiple images
    # This is a temporary ship-asap solution
    avatar_uri: Mapped[str] = mapped_column(nullable=True)
    long_description: Mapped[str] = mapped_column(nullable=True)
    greeting_message: Mapped[str] = mapped_column(nullable=True)
    is_active: Mapped[bool] = mapped_column(default=True)
    is_public: Mapped[bool] = mapped_column(default=False)
    is_short_description_public: Mapped[bool] = mapped_column(default=True)
    is_long_description_public: Mapped[bool] = mapped_column(default=False)
    is_greeting_message_public: Mapped[bool] = mapped_column(default=True)
    embedding: Mapped[list[float]] = mapped_column(nullable=True, default=None)
    embedding_model: Mapped[str] = mapped_column(nullable=True, default=None)
    num_messages: Mapped[int] = mapped_column(default=0)
    num_conversations: Mapped[int] = mapped_column(default=0)
    tags: Mapped[list["Tag"]] = relationship(
        secondary=clones_to_tags, back_populates="clones", lazy="joined"
    )
    creator_id: Mapped[uuid.UUID] = mapped_column(
        sa.ForeignKey("creators.user_id", ondelete="cascade"), nullable=False
    )
    creator: Mapped["Creator"] = relationship("Creator", back_populates="clones")
    users: Mapped[list["User"]] = relationship(
        secondary=users_to_clones, back_populates="clones"
    )
    # api_keys: Mapped[list["APIKey"]] = relationship("APIKey", back_populates="clone")
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
    monologues: Mapped[list["Monologue"]] = relationship(
        "Monologue", back_populates="clone"
    )
    memories: Mapped[list["Memory"]] = relationship("Memory", back_populates="clone")
    agent_summaries: Mapped[list["AgentSummary"]] = relationship(
        "AgentSummary", back_populates="clone"
    )
    entity_context_summaries: Mapped[list["EntityContextSummary"]] = relationship(
        "EntityContextSummary", back_populates="clone"
    )
    llm_calls: Mapped[list["LLMCall"]] = relationship(
        "LLMCall", back_populates="clone", passive_deletes=True
    )

    # taken from https://docs.sqlalchemy.org/en/20/orm/extensions/hybrid.html#building-custom-comparators
    # these automatically lowercase everything in a comparison
    @hybrid_property
    def case_insensitive_name(self) -> str:
        return self.name.lower()

    @case_insensitive_name.inplace.comparator
    @classmethod
    def _case_insensitive_comparator(cls) -> CaseInsensitiveComparator:
        return CaseInsensitiveComparator(cls.name)

    def __repr__(self):
        return f"Clone(clone_id={self.id}, active={self.is_active}, public={self.is_public})"


_ = sa.Index("ix_clones_case_insensitive_name", Clone.case_insensitive_name)


# I need to rewrite the dockerfile to install the pg_trm extension. Don't wanna do that.
# clone_trigram_index = sa.Index(
#     "idx_clones_case_insensitive_name_trigram",
#     Clone.case_insensitive_name,
#     postgresql_using="gin",
#     postgresql_ops={"case_insensitive_name": "gin_trgm_ops"},
# )


class Conversation(CommonMixin, Base):
    __tablename__ = "conversations"

    # (Jonny) is the name field necessary?
    name: Mapped[str] = mapped_column(default=randomname.get_name)
    is_active: Mapped[bool] = mapped_column(default=True)
    # Multi-user chat is hard to configure, maybe we have API-key validation
    # only for those, and just charge the api-key per minute
    user_name: Mapped[str]
    memory_strategy: Mapped[str]
    information_strategy: Mapped[str]
    plasticity: Mapped[int]
    user_id: Mapped[uuid.UUID] = mapped_column(
        sa.ForeignKey("users.id", ondelete="cascade"), nullable=False
    )
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
    llm_calls: Mapped[list["LLMCall"]] = relationship(
        "LLMCall", back_populates="conversation", passive_deletes=True
    )

    def __repr__(self):
        return f"Conversation(name={self.name}, user_id={self.user_id} clone_id={self.clone_id})"


class Message(CommonMixin, Base):
    __tablename__ = "messages"

    content: Mapped[str]
    sender_name: Mapped[str]
    is_clone: Mapped[bool]
    timestamp: Mapped[datetime.datetime] = mapped_column(
        sa.DateTime(timezone=True), server_default=sa.func.now()
    )
    embedding: Mapped[list[float]] = mapped_column(nullable=True)
    embedding_model: Mapped[str] = mapped_column(nullable=True)
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

    @hybrid_property
    def case_insensitive_content(self) -> str:
        return self.content.lower()

    @case_insensitive_content.inplace.comparator
    @classmethod
    def _case_insensitive_comparator(cls) -> CaseInsensitiveComparator:
        return CaseInsensitiveComparator(cls.content)

    def __repr__(self):
        return f"Message(content={self.content}, sender={self.sender_name}, is_clone={self.from_clone})"


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
    embedding: Mapped[list[float]]
    embedding_model: Mapped[str]
    clone_id: Mapped[uuid.UUID] = mapped_column(
        sa.ForeignKey("clones.id", ondelete="cascade"), nullable=False
    )
    clone: Mapped["Clone"] = relationship("Clone", back_populates="documents")
    nodes: Mapped[list["Node"]] = relationship(
        "Node", back_populates="document", cascade="all, delete"
    )

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
    embedding: Mapped[list[float]]
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
        sa.ForeignKey("clones.id"), nullable=False
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
    embedding: Mapped[list[float]]
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
    embedding: Mapped[list[float]]
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


class Monologue(CommonMixin, Base):
    """These are single line examples of clone speech. Since it's one-way,
    we don't need any information on the clone. A max char limit is imposed."""

    __tablename__ = "monologues"

    content: Mapped[str]
    source: Mapped[str]
    hash: Mapped[str]
    embedding: Mapped[list[float]]
    embedding_model: Mapped[str]
    clone_id: Mapped[uuid.UUID] = mapped_column(
        sa.ForeignKey("clones.id", ondelete="cascade"), nullable=False
    )
    clone: Mapped["Clone"] = relationship("Clone", back_populates="monologues")

    def __repr__(self):
        name = self.__class__.__name__
        content = self.content
        msg = f"... + {len(content) - 30} chars"
        if len(content) > 30 + len(msg):
            content = content[:30] + msg
        return f"{name}(source={self.source}, content={content})"


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
    embedding: Mapped[list[float]]
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


class LLMCall(CommonMixin, Base):
    __tablename__ = "llm_calls"

    content: Mapped[str]
    model_type: Mapped[str]
    model_name: Mapped[str]
    prompt_tokens: Mapped[int]
    completion_tokens: Mapped[int]
    total_tokens: Mapped[int]
    duration: Mapped[float]
    role: Mapped[str]
    tokens_per_second: Mapped[float]
    input_prompt: Mapped[str]
    # Any time a generate template is called
    template: Mapped[str] = mapped_column(nullable=True)
    # number of retries for calls that require output parsing
    retry_attempt: Mapped[int] = mapped_column(nullable=True)
    # Metadata from LongDescription generation
    document_id: Mapped[uuid.UUID] = mapped_column(
        sa.ForeignKey("documents.id", ondelete="SET NULL"),
        nullable=False,
        server_default=None,
    )
    # Metadata from Indexing
    chunk_index: Mapped[int] = mapped_column(nullable=True)
    depth: Mapped[int] = mapped_column(nullable=True)
    subroutine: Mapped[str] = mapped_column(nullable=True)
    group: Mapped[int] = mapped_column(nullable=True)
    # Track usage and costs on a particular clone.
    # Note, creator stats require a join
    clone_id: Mapped[uuid.UUID] = mapped_column(
        sa.ForeignKey("clones.id", ondelete="SET NULL"),
        nullable=False,
        server_default=None,
    )
    # Track usage and costs incurred by any particular user
    user_id: Mapped[uuid.UUID] = mapped_column(
        sa.ForeignKey("users.id", ondelete="SET NULL"),
        nullable=False,
        server_default=None,
    )
    # Track usage and costs within a conversation
    conversation_id: Mapped[uuid.UUID] = mapped_column(
        sa.ForeignKey("conversations.id", ondelete="SET NULL"),
        nullable=False,
        server_default=None,
    )
    clone: Mapped["Clone"] = relationship("Clone", back_populates="llm_calls")
    user: Mapped["User"] = relationship("User", back_populates="llm_calls")
    conversation: Mapped["Conversation"] = relationship(
        "Conversation", back_populates="llm_calls"
    )


# ------------- Stripe ------------- #
# class UsageRecord(CommonMixin, Base):
#     __tablename__ = "usage_records"

#     user_id: Mapped[uuid.UUID] = mapped_column(
#         sa.ForeignKey("users.id", ondelete="cascade"), nullable=False
#     )
#     subscription_id: Mapped[uuid.UUID] = mapped_column(
#         sa.ForeignKey("subscriptions.id", ondelete="cascade"), nullable=False
#     )
#     quantity: Mapped[int] = mapped_column(sa.Integer, nullable=False)
#     timestamp: Mapped[datetime.datetime] = mapped_column(nullable=True)


# class Subscription(CommonMixin, Base):
#     __tablename__ = "subscriptions"

#     # Should match Stripe's subscription id
#     subscription_id: Mapped[str] = mapped_column(nullable=False)
#     customer_id: Mapped[str] = mapped_column(nullable=False)
#     user_id: Mapped[uuid.UUID] = mapped_column(
#         sa.ForeignKey("users.id", ondelete="cascade"), nullable=False
#     )
#     stripe_status: Mapped[str] = mapped_column(nullable=False)
#     stripe_created: Mapped[datetime.datetime]
#     stripe_current_period_start: Mapped[datetime.datetime]
#     stripe_current_period_end: Mapped[datetime.datetime]
#     stripe_cancel_at_period_end: Mapped[bool]
#     stripe_canceled_at: Mapped[datetime.datetime]


# ### Moderation
# class ModerationRecord(CommonMixin, Base):
#     __tablename__ = "moderation_records"

#     user_id: Mapped[uuid.UUID] = mapped_column(
#         sa.ForeignKey("users.id", ondelete="cascade"), nullable=False
#     )
#     violation_content: Mapped[str] = mapped_column(nullable=False)
#     is_banned: Mapped[bool] = mapped_column(nullable=False)


# ### Signups


# class CreatorPartnerProgramSignup(Base):
#     __tablename__ = "creator_partner_signups"

#     id: Mapped[uuid.UUID] = mapped_column(
#         primary_key=True, server_default=sa.text("gen_random_uuid()")
#     )
#     user_id: Mapped[uuid.UUID] = mapped_column(
#         sa.ForeignKey("users.id", ondelete="cascade"), nullable=False
#     )
#     name: Mapped[str] = mapped_column(sa.String, nullable=False)
#     email: Mapped[str] = mapped_column(sa.String, nullable=False)
#     phone: Mapped[str] = mapped_column(sa.String, nullable=False)
#     social_media_handles: Mapped[str] = mapped_column(sa.String, nullable=False)

#     user = relationship("User", back_populates="creator_partner_signup")

#     def __repr__(self):
#         return f"CreatorPartnerSignup(id={self.id}, user_id={self.user_id}, name='{self.name}', email='{self.email}')"


# class NSFWSignup(CommonMixin, Base):
#     __tablename__ = "nsfw_signups"

#     user_id: Mapped[uuid.UUID] = mapped_column(
#         sa.ForeignKey("users.id", ondelete="cascade"), nullable=False
#     )
#     name: Mapped[str] = mapped_column(sa.String, nullable=False)
#     email: Mapped[str] = mapped_column(sa.String, nullable=False)
#     phone: Mapped[str] = mapped_column(sa.String, nullable=False)
#     social_media_handles: Mapped[str] = mapped_column(sa.String, nullable=False)

#     user = relationship("User", back_populates="nsfw_signup")

#     def __repr__(self):
#         return f"NSFWSignup(id={self.id}, user_id={self.user_id}, name='{self.name}', email='{self.email}')"
