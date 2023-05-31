import datetime
import uuid

import randomname
from fastapi_users.db import (
    SQLAlchemyBaseOAuthAccountTableUUID,
    SQLAlchemyBaseUserTableUUID,
)
from sqlalchemy import CheckConstraint, DateTime, ForeignKey, func, text
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, relationship


class Base(DeclarativeBase):
    pass


class OAuthAccount(SQLAlchemyBaseOAuthAccountTableUUID, Base):
    user_id: Mapped[uuid.UUID] = mapped_column(
        ForeignKey("users.id", ondelete="cascade"), nullable=False
    )


class User(Base, SQLAlchemyBaseUserTableUUID):
    __tablename__ = "users"
    oauth_accounts: Mapped[list[OAuthAccount]] = relationship(
        "OAuthAccount", lazy="joined"
    )
    clones: Mapped[list["Clone"]] = relationship("Clone", lazy="joined")

    def __repr__(self):
        return f"User(id={self.id}, oauth_accounts={self.oauth_accounts}, clones={self.clones})"


class CommonMixin:
    id: Mapped[uuid.UUID] = mapped_column(
        primary_key=True, server_default=text("gen_random_uuid()")
    )
    created_at: Mapped[datetime.datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now()
    )
    updated_at: Mapped[datetime.datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        onupdate=func.current_timestamp(),
    )


class Clone(CommonMixin, Base):
    __tablename__ = "clones"

    name: Mapped[str]
    greeting_message: Mapped[str]
    is_active: Mapped[bool] = mapped_column(default=True)
    is_public: Mapped[bool] = mapped_column(default=False)
    user_id: Mapped[uuid.UUID] = mapped_column(
        ForeignKey("users.id", ondelete="cascade"), nullable=False
    )
    user: Mapped["User"] = relationship("User", back_populates="clones")
    conversations: Mapped[list["Conversation"]] = relationship(
        "Conversation", lazy="select"
    )
    api_keys: Mapped[list["APIKey"]] = relationship("APIKey", lazy="select")

    def __repr__(self):
        return f"Clone(clone_id={self.id}, active={self.is_active}, public={self.is_public})"


class APIKey(CommonMixin, Base):
    __tablename__ = "api_keys"

    hashed_key: Mapped[str] = mapped_column(unique=True)
    name: Mapped[str] = mapped_column(default=randomname.get_name)
    clone_id: Mapped[uuid.UUID] = mapped_column(
        ForeignKey("clones.id", ondelete="cascade"), nullable=False
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

    def __repr__(self):
        return f"Conversation(name={self.name}, clone_id={self.clone_id})"


class Message(CommonMixin, Base):
    __tablename__ = "messages"

    content: Mapped[str]
    sender_name: Mapped[str]
    from_clone: Mapped[bool] = mapped_column(default=False)
    conversation_id: Mapped[uuid.UUID] = mapped_column(
        ForeignKey("conversations.id", ondelete="cascade"), nullable=False
    )
    conversation: Mapped["Conversation"] = relationship(
        "Conversation", back_populates="messages"
    )

    def __repr__(self):
        return f"Message(content={self.content}, sender={self.sender}, from_clone={self.from_clone})"


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
