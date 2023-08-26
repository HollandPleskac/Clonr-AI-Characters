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

from clonr.utils.formatting import DateFormat


class CaseInsensitiveComparator(Comparator[str]):
    # taken from https://docs.sqlalchemy.org/en/20/orm/extensions/hybrid.html#building-custom-comparators
    def __eq__(self, other: Any) -> sa.ColumnElement[bool]:  # type: ignore[override]  # noqa: E501
        return sa.func.lower(self.__clause_element__()) == sa.func.lower(other)

    def ilike(
        self, other: Any, escape: str | None = None, **kwargs
    ) -> sa.BinaryExpression[bool]:
        return sa.func.lower(self.__clause_element__()).ilike(
            other.lower(), escape=escape, **kwargs
        )

    def like(
        self, other: Any, escape: str | None = None, **kwargs
    ) -> sa.BinaryExpression[bool]:
        return sa.func.lower(self.__clause_element__()).like(
            other.lower(), escape=escape, **kwargs
        )

    def levenshtein(self, other: Any, **kwargs) -> sa.ColumnElement[int]:
        return sa.func.levenshtein(
            sa.func.lower(self.__clause_element__()), other.lower()
        )

    def similarity(self, other: Any, **kwargs) -> sa.ColumnElement[float]:
        return sa.func.similarity(
            sa.func.lower(self.__clause_element__()), other.lower(), **kwargs
        )

    def word_similarity(self, other: Any, **kwargs) -> sa.ColumnElement[float]:
        return sa.func.word_similarity(
            other.lower(), sa.func.lower(self.__clause_element__()), **kwargs
        )

    def strict_word_similarity(self, other: Any, **kwargs) -> sa.ColumnElement[float]:
        return sa.func.strict_word_similarity(
            other.lower(), sa.func.lower(self.__clause_element__()), **kwargs
        )

    def operate(self, op: Any, *other: Any, **kwargs: Any) -> sa.ColumnElement[Any]:
        return sa.func.lower(self.__clause_element__()).operate(op, *other, **kwargs)


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
    # FixMe: (Jonny) I remember this being an issue during migrations, where we have to edit the first db
    # migration to use fastapi_users GUID, but I cannot figure out how to solve this type issue
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
    # Whether user is subscribed to premium plan, i.e. is paid
    stripe_customer_id: Mapped[str] = mapped_column(nullable=True)
    nsfw_enabled: Mapped[bool] = mapped_column(default=False)
    # Number of free msgs sent
    num_free_messages_sent: Mapped[int] = mapped_column(default=0)
    # (Jonny): Idk why, but select breaks with greenlet spawn error and this doesn't
    oauth_accounts: Mapped[list[OAuthAccount]] = relationship(
        "OAuthAccount", lazy="joined"
    )
    # (Jonny): probably never a situation where you don't need clones when grabbing a user.
    clones: Mapped[list["Clone"]] = relationship(
        secondary=users_to_clones, back_populates="users"
    )
    messages: Mapped[list["Message"]] = relationship("Message", back_populates="user")
    conversations: Mapped[list["Conversation"]] = relationship(
        "Conversation", back_populates="user"
    )
    creator: Mapped["Creator"] = relationship("Creator", back_populates="user")
    llm_calls: Mapped[list["LLMCall"]] = relationship(
        "LLMCall", back_populates="user", passive_deletes=True
    )
    subscriptions: Mapped[list["Subscription"]] = relationship(
        "Subscription", back_populates="user"
    )

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


clones_to_tags = sa.Table(
    "clones_to_tags",
    Base.metadata,
    sa.Column("tag_id", sa.Integer, sa.ForeignKey("tags.id"), primary_key=True),
    sa.Column("clone_id", sa.Uuid, sa.ForeignKey("clones.id"), primary_key=True),
)


class Tag(Base):
    __tablename__ = "tags"

    id: Mapped[int] = mapped_column(autoincrement=True, primary_key=True)
    created_at: Mapped[datetime.datetime] = mapped_column(
        sa.DateTime(timezone=True), server_default=sa.func.now()
    )
    updated_at: Mapped[datetime.datetime] = mapped_column(
        sa.DateTime(timezone=True),
        server_default=sa.func.now(),
        onupdate=sa.func.current_timestamp(),
    )
    name: Mapped[str] = mapped_column(unique=True)
    color_code: Mapped[str] = mapped_column(nullable=True)
    clones: Mapped[list["Clone"]] = relationship(
        secondary=clones_to_tags, back_populates="tags"
    )

    def __repr__(self):
        return f"Tag(id={self.id}, name={self.name}, color_code={self.color_code})"


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
    generated_long_descriptions: Mapped[list["LongDescription"]] = relationship(
        "LongDescription", back_populates="clone"
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


# Use gin since we have fewer elements and fewer fluctuations
# this will also speed up LIKE and ILIKE statements
ix_clones_case_insensitive_name = sa.Index(
    "ix_clones_case_insensitive_name",
    sa.text("lower(clones.name) gin_trgm_ops"),
    postgresql_using="gin",
    postgresql_ops={"name": "gin_trgm_ops"},
)


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
    agent_summary_threshold: Mapped[int] = mapped_column(nullable=True)
    reflection_threshold: Mapped[int] = mapped_column(nullable=True)
    entity_context_threshold: Mapped[int] = mapped_column(nullable=True)
    adaptation_strategy: Mapped[str] = mapped_column(nullable=True)
    # NOTE (Jonny): data redundancy, but it will allow us to not perform an expensive join on messages when fetching convos
    # this serves 2 purposes: (1) eliminates a join (2) by updating this, is auto triggers the last_updated_at field on this model!
    last_message: Mapped[str] = mapped_column(nullable=True)
    # total num messages ever sent/received, including inactive ones
    num_messages_ever: Mapped[int] = mapped_column(default=0)
    user_id: Mapped[uuid.UUID] = mapped_column(
        sa.ForeignKey("users.id", ondelete="cascade"), nullable=False
    )
    # NOTE (Jonny): decided against this, since we would also need an event to trigger
    # on message update to recompute the number of messages that are active. Too complicated for now
    # num_messages: Mapped[int] = mapped_column(default=0)
    user: Mapped["User"] = relationship("User", back_populates="conversations")
    # NOTE (Jonny): data redundancy, but it will allow us to not perform an expensive join when fetching convos
    # since users cannot change a clone name without deleting, there should be no worry about this being in sync
    clone_name: Mapped[str]
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

    @hybrid_property
    def case_insensitive_clone_name(self) -> str:
        return self.clone_name.lower()

    @case_insensitive_clone_name.inplace.comparator
    @classmethod
    def _case_insensitive_comparator(cls) -> CaseInsensitiveComparator:
        return CaseInsensitiveComparator(cls.clone_name)

    def __repr__(self):
        return f"Conversation(clone_name={self.clone_name}, user_name={self.user_name}, user_id={self.user_id} clone_id={self.clone_id})"


# class Temp(Base):
#     __tablename__ = "temp"

#     id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
#     name: Mapped[str]
#     name2: Mapped[str]

#     # is_main: Mapped[bool] = mapped_column(default=True)
#     # parent_id: Mapped[int] = mapped_column(sa.ForeignKey("temp.id"), nullable=True)
#     # parent: Mapped["Temp"] = relationship(
#     #     "Temp", back_populates="children", remote_side="Temp.id"
#     # )
#     # children: Mapped[list["Temp"]] = relationship("Temp", back_populates="parent")
#     @hybrid_property
#     def case_insensitive_name(self) -> str:
#         return self.name.lower()

#     @case_insensitive_name.inplace.comparator
#     @classmethod
#     def _case_insensitive_comparator(cls) -> CaseInsensitiveComparator:
#         return CaseInsensitiveComparator(cls.name)

#     def __repr__(self):
#         return f"Temp(name={self.name}, id={self.id})"


# temp_trgm_index = sa.Index(
#     "temp_trgm_idx",
#     Temp.case_insensitive_name,
#     postgresql_using="gist",
#     postgresql_ops={"name": "gist_trgm_ops"},
# )

# temp_trgm_index2 = sa.Index(
#     "temp_trgm_idx2",
#     Temp.case_insensitive_name,
#     postgresql_using="gin",
#     postgresql_ops={"name": "gin_trgm_ops"},
# )


class Message(CommonMixin, Base):
    __tablename__ = "messages"

    content: Mapped[str]
    sender_name: Mapped[str]
    is_clone: Mapped[bool]
    is_main: Mapped[bool] = mapped_column(default=True)
    is_active: Mapped[bool] = mapped_column(default=True)
    timestamp: Mapped[datetime.datetime] = mapped_column(
        sa.DateTime(timezone=True), server_default=sa.func.now()
    )
    embedding: Mapped[list[float]] = mapped_column(nullable=True)
    embedding_model: Mapped[str] = mapped_column(nullable=True)
    parent_id: Mapped[uuid.UUID] = mapped_column(
        sa.ForeignKey("messages.id"), nullable=True
    )
    parent: Mapped["Message"] = relationship(
        "Message", back_populates="children", remote_side="Message.id"
    )
    children: Mapped[list["Message"]] = relationship("Message", back_populates="parent")
    clone_id: Mapped[uuid.UUID] = mapped_column(
        sa.ForeignKey("clones.id", ondelete="cascade"), nullable=False
    )
    clone: Mapped["Clone"] = relationship("Clone", back_populates="messages")
    user_id: Mapped[uuid.UUID] = mapped_column(
        sa.ForeignKey("users.id", ondelete="cascade"), nullable=False
    )
    user: Mapped["User"] = relationship("User", back_populates="messages")
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

    @property
    def time_str(self) -> str:
        # return DateFormat.relative(self.timestamp, n_largest_times=2)
        return DateFormat.human_readable(self.timestamp, use_today_and_yesterday=True)

    def __repr__(self):
        return f"Message(content={self.content}, sender={self.sender_name}, is_clone={self.is_clone})"


# (Jonny) gist has faster updates than gin, which is what we want for messages!
msg_case_insensitive_content_trgm_index = sa.Index(
    "msg_case_insensitive_content_trgm_index",
    sa.text("lower(messages.name) gist_trgm_ops"),
    postgresql_using="gist",
    postgresql_ops={"name": "gist_trgm_ops"},
)


long_descs_to_docs = sa.Table(
    "long_descs_to_docs",
    Base.metadata,
    sa.Column("document_id", sa.ForeignKey("documents.id"), primary_key=True),
    sa.Column(
        "long_description_id", sa.ForeignKey("long_descriptions.id"), primary_key=True
    ),
)


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
    generated_long_descriptions: Mapped[list["LongDescription"]] = relationship(
        secondary=long_descs_to_docs, back_populates="documents"
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
        sa.DateTime(timezone=True),
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

    @property
    def time_str(self) -> str:
        # return DateFormat.relative(self.timestamp, n_largest_times=2)
        return DateFormat.human_readable(self.timestamp)

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
    http_retry_attempt: Mapped[int] = mapped_column(nullable=True)
    # Metadata from LongDescription generation
    document_id: Mapped[uuid.UUID | None] = mapped_column(
        sa.ForeignKey("documents.id", ondelete="SET NULL"),
        nullable=True,
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
    # TODO (Jonny): if we don't allow users to delete themselves,
    # this is probably safe to make cascade-delete.
    user_id: Mapped[uuid.UUID] = mapped_column(
        sa.ForeignKey("users.id", ondelete="cascade"),
        nullable=False,
        server_default=None,
    )
    # Track usage and costs within a conversation
    conversation_id: Mapped[uuid.UUID | None] = mapped_column(
        sa.ForeignKey("conversations.id", ondelete="SET NULL"),
        nullable=True,
        server_default=None,
    )
    clone: Mapped["Clone"] = relationship("Clone", back_populates="llm_calls")
    user: Mapped["User"] = relationship("User", back_populates="llm_calls")
    conversation: Mapped["Conversation"] = relationship(
        "Conversation", back_populates="llm_calls"
    )

    def __repr__(self):
        content = self.content
        if len(content) < 80:
            content = content[:50] + " ..."
        return f"LLMCall(subroutine={self.subroutine}, duration={self.duration}, prompt_tokens={self.prompt_tokens}, total_tokens={self.total_tokens}, content={self.content})"


class ContentViolation(CommonMixin, Base):
    __tablename__ = "content_violations"

    content: Mapped[str]
    reasons: Mapped[str] = mapped_column(default="")
    user_id: Mapped[uuid.UUID] = mapped_column(
        sa.ForeignKey("users.id", ondelete="cascade"), nullable=False
    )
    clone_id: Mapped[uuid.UUID] = mapped_column(
        sa.ForeignKey("clones.id", ondelete="SET NULL")
    )
    conversation_id: Mapped[uuid.UUID] = mapped_column(
        sa.ForeignKey("conversations.id", ondelete="SET NULL")
    )


class LongDescription(CommonMixin, Base):
    __tablename__ = "long_descriptions"

    content: Mapped[str]
    documents: Mapped[list["Document"]] = relationship(
        secondary=long_descs_to_docs, back_populates="generated_long_descriptions"
    )
    clone_id: Mapped[uuid.UUID] = mapped_column(
        sa.ForeignKey("clones.id", ondelete="cascade")
    )
    clone: Mapped["Clone"] = relationship(
        "Clone", back_populates="generated_long_descriptions"
    )


# ------------- Stripe ------------- #
# TODO (Jonny): add a field for scheduled to be canceled
class Subscription(CommonMixin, Base):
    __tablename__ = "subscriptions"

    stripe_subscription_id: Mapped[str] = mapped_column(
        nullable=False, primary_key=True
    )
    created_at: Mapped[datetime.datetime] = mapped_column(
        sa.DateTime(timezone=True), server_default=sa.func.now()
    )
    updated_at: Mapped[datetime.datetime] = mapped_column(
        sa.DateTime(timezone=True),
        server_default=sa.func.now(),
        onupdate=sa.func.current_timestamp(),
    )
    amount: Mapped[int]
    currency: Mapped[str]
    interval: Mapped[str]
    stripe_customer_id: Mapped[str]
    stripe_subscription_id: Mapped[str]
    stripe_status: Mapped[str]
    stripe_created: Mapped[int]
    stripe_current_period_start: Mapped[int]
    stripe_current_period_end: Mapped[int]
    stripe_quantity: Mapped[int]
    stripe_price_id: Mapped[str]
    stripe_price_lookup_key: Mapped[str]
    stripe_product_id: Mapped[str]
    stripe_product_name: Mapped[str]
    stripe_cancel_at_period_end: Mapped[bool]
    user_id: Mapped[uuid.UUID] = mapped_column(
        sa.ForeignKey("users.id", ondelete="cascade"), nullable=False
    )
    user: Mapped["User"] = relationship("User", back_populates="subscriptions")


class CreatorPartnerProgramSignup(CommonMixin, Base):
    __tablename__ = "creator_partner_signups"

    id: Mapped[int] = mapped_column(autoincrement=True, primary_key=True)
    created_at: Mapped[datetime.datetime] = mapped_column(
        sa.DateTime(timezone=True), server_default=sa.func.now()
    )
    updated_at: Mapped[datetime.datetime] = mapped_column(
        sa.DateTime(timezone=True),
        server_default=sa.func.now(),
        onupdate=sa.func.current_timestamp(),
    )
    email: Mapped[str]
    nsfw: Mapped[bool] = mapped_column(nullable=True)
    personal: Mapped[bool] = mapped_column(nullable=True)
    quality: Mapped[bool] = mapped_column(nullable=True)
    story: Mapped[bool] = mapped_column(nullable=True)
    roleplay: Mapped[bool] = mapped_column(nullable=True)
    user_id: Mapped[uuid.UUID] = mapped_column(
        sa.ForeignKey("users.id", ondelete="cascade"), nullable=False
    )

    def __repr__(self):
        arr = [
            ("user_id", self.user_id),
            ("nsfw", self.nsfw),
            ("personal", self.personal),
            ("quality", self.quality),
            ("story", self.story),
            ("roleplay", self.roleplay),
        ]
        arr2 = [f"{x}={y}" for x, y in arr if y is not None]
        args = ", ".join(arr2)
        return f"CreatorPartnerProgramSignup({args})"


class ClonrPlusSignup(Base):
    __tablename__ = "clonr_plus_signups"

    id: Mapped[int] = mapped_column(autoincrement=True, primary_key=True)
    created_at: Mapped[datetime.datetime] = mapped_column(
        sa.DateTime(timezone=True), server_default=sa.func.now()
    )
    updated_at: Mapped[datetime.datetime] = mapped_column(
        sa.DateTime(timezone=True),
        server_default=sa.func.now(),
        onupdate=sa.func.current_timestamp(),
    )
    email: Mapped[str]
    nsfw: Mapped[bool] = mapped_column(nullable=True)
    long_term_memory: Mapped[bool] = mapped_column(nullable=True)
    greater_accuracy: Mapped[bool] = mapped_column(nullable=True)
    multiline_chat: Mapped[bool] = mapped_column(nullable=True)
    user_id: Mapped[uuid.UUID] = mapped_column(
        sa.ForeignKey("users.id", ondelete="cascade"), nullable=False
    )

    def __repr__(self):
        arr = [
            ("user_id", self.user_id),
            ("nsfw", self.nsfw),
            ("long_term_memory", self.long_term_memory),
            ("greater_accuracy", self.greater_accuracy),
            ("multiline_chat", self.multiline_chat),
        ]
        arr2 = [f"{x}={y}" for x, y in arr if y is not None]
        args = ", ".join(arr2)
        return f"ClonrPlusSignup({args})"
