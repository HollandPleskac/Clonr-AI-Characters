import datetime
import uuid

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
    api_keys: Mapped[list["APIKey"]] = relationship("APIKey", lazy="joined")
    conversations: Mapped[list["Conversation"]] = relationship(
        "Conversation", lazy="joined"
    )


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

    is_active: Mapped[bool] = mapped_column(default=True)
    is_public: Mapped[bool] = mapped_column(default=False)

    # train_audio_minutes: Mapped[float]
    # audio_uri: Mapped[str] = mapped_column(nullable=False)

    user_id: Mapped[uuid.UUID] = mapped_column(
        ForeignKey("users.id", ondelete="cascade"), nullable=False
    )

    conversations: Mapped[list["Conversation"]] = relationship(
        "Conversation", lazy="joined"
    )
    user: Mapped["User"] = relationship("User", back_populates="clones")
    api_keys: Mapped[list["APIKey"]] = relationship("APIKey", lazy="joined")

    def __repr__(self):
        return f"Clone(clone_id={self.id}, active={self.is_active}, public={self.is_public}"


class APIKey(CommonMixin, Base):
    __tablename__ = "api_keys"

    key: Mapped[str] = mapped_column(nullable=False)
    is_active: Mapped[bool] = mapped_column(default=True)
    user_id: Mapped[uuid.UUID] = mapped_column(
        ForeignKey("users.id", ondelete="cascade"), nullable=False
    )
    clone_id: Mapped[uuid.UUID] = mapped_column(
        ForeignKey("clones.id", ondelete="cascade"), nullable=False
    )

    user: Mapped["User"] = relationship("User", back_populates="api_keys")
    clone: Mapped["Clone"] = relationship("Clone", back_populates="api_keys")

    def __repr__(self):
        return f"APIKey(api_key={self.key}, active={self.is_active}, user_id={self.user_id}, clone_id={self.clone_id})"


class Conversation(CommonMixin, Base):
    __tablename__ = "conversations"

    user_id: Mapped[uuid.UUID] = mapped_column(
        ForeignKey("users.id", ondelete="cascade"), nullable=False
    )
    clone_id: Mapped[uuid.UUID] = mapped_column(
        ForeignKey("clones.id", ondelete="cascade"), nullable=False
    )

    messages: Mapped[list["Message"]] = relationship("Message", lazy="joined")
    user: Mapped["User"] = relationship("User", back_populates="conversations")
    clone: Mapped["Clone"] = relationship("Clone", back_populates="conversations")

    def __repr__(self):
        return f"Conversation(user_id={self.user_id}, clone_id={self.clone_id})"


class Message(CommonMixin, Base):
    __tablename__ = "messages"
    __table_args__ = (CheckConstraint("NOT(user_id IS NULL AND clone_id IS NULL)"),)

    user_id: Mapped[uuid.UUID] = mapped_column(
        ForeignKey("users.id", ondelete="cascade"), nullable=True
    )
    clone_id: Mapped[uuid.UUID] = mapped_column(
        ForeignKey("clones.id", ondelete="cascade"), nullable=True
    )
    message: Mapped[str]
    conversation_id: Mapped[uuid.UUID] = mapped_column(
        ForeignKey("conversations.id", ondelete="cascade"), nullable=False
    )
    conversation: Mapped["Conversation"] = relationship(
        "Conversation", back_populates="messages"
    )

    def __repr__(self):
        return f"Message(message={self.message}, conversation_id={self.conversation_id}, user_id={self.user_id}, clone_id={self.clone_id})"


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
