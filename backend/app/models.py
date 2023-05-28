import datetime
import uuid

from fastapi_users.db import (
    SQLAlchemyBaseOAuthAccountTableUUID,
    SQLAlchemyBaseUserTableUUID,
)
from sqlalchemy import DateTime, ForeignKey, func, text
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, relationship


class Base(DeclarativeBase):
    pass


class OAuthAccount(SQLAlchemyBaseOAuthAccountTableUUID, Base):
    user_id: Mapped[uuid.UUID] = mapped_column(
        ForeignKey("user.id", ondelete="cascade"), nullable=False
    )


class User(Base, SQLAlchemyBaseUserTableUUID):
    __tablename__ = "user"
    oauth_accounts: Mapped[list[OAuthAccount]] = relationship(
        "OAuthAccount", lazy="joined"
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


# class Clone(CommonMixin, Base):
#     __tablename__ = "clones"

#     active: Mapped[bool] = mapped_column(default=False)
#     train_audio_minutes: Mapped[float]
#     audio_bucket: Mapped[str] = mapped_column(nullable=False)
#     user_id: Mapped[uuid.UUID] = mapped_column(
#         ForeignKey("users.id", ondelete="cascade"), nullable=False
#     )

#     user: Mapped["User"] = relationship("User", back_populates="clones")

#     def __repr__(self):
#         return f"Clone(clone_id={self.clone_id}, active={self.active}"


# class User(CommonMixin, Base):
#     __tablename__ = "users"

#     email: Mapped[str] = mapped_column(unique=True, nullable=False)
#     active: Mapped[bool] = mapped_column(default=True)
#     is_superuser: Mapped[bool] = mapped_column(default=False)

#     clones: Mapped[list["Clone"]] = relationship("Clone", back_populates="user")
#     conversations: Mapped[list["Conversation"]] = relationship(
#         "Conversation", back_populates="user"
#     )

#     def __repr__(self):
#         return f"User(email={self.email}, active={self.active}"


# class Conversation(CommonMixin, Base):
#     __tablename__ = "conversations"

#     user_id: Mapped[uuid.UUID] = mapped_column(
#         ForeignKey("users.id", ondelete="cascade"), nullable=False
#     )
#     clone_id: Mapped[uuid.UUID] = mapped_column(
#         ForeignKey("clones.id", ondelete="cascade"), nullable=False
#     )

#     user: Mapped["User"] = relationship("User", back_populates="conversations")
#     clone: Mapped["Clone"] = relationship("Clone", back_populates="conversations")
#     messages: Mapped[list["Message"]] = relationship(
#         "Message", back_populates="conversations"
#     )


# class Message(CommonMixin, Base):
#     __tablename__ = "messages"

#     content: Mapped[str] = mapped_column(nullable=False)
#     conversation_id: Mapped[uuid.UUID] = mapped_column(
#         ForeignKey("conversations.id", ondelete="cascade"),
#         nullable=False,
#     )
#     user_id: Mapped[uuid.UUID] = mapped_column(
#         ForeignKey("users.id", ondelete="cascade"), nullable=False
#     )

#     user: Mapped["User"] = relationship("User", back_populates="messages")
#     conversation: Mapped["Conversation"] = relationship(
#         "Conversation", back_populates="messages"
#     )


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
