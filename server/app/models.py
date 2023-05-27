import datetime
import uuid

from sqlalchemy import DateTime, ForeignKey, func, text
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, relationship


class Base(DeclarativeBase):
    pass


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

    clone_id: Mapped[str] = mapped_column(unique=True, nullable=False)
    active: Mapped[bool] = mapped_column(default=False)
    min_training_audio: Mapped[float]
    audio_bucket: Mapped[str] = mapped_column(nullable=False)
    user_id: Mapped[uuid.UUID] = mapped_column(
        ForeignKey("users.id", ondelete="cascade"), nullable=False
    )

    user = relationship("User", back_populates="clones")

    def __repr__(self):
        return f"Clone(clone_id={self.clone_id}, active={self.active}"


class User(CommonMixin, Base):
    __tablename__ = "users"

    email: Mapped[str] = mapped_column(unique=True, nullable=False)
    active: Mapped[bool] = mapped_column(default=True)
    is_superuser: Mapped[bool] = mapped_column(default=False)

    clones = relationship("Clone", back_populates="user")

    def __repr__(self):
        return f"User(email={self.email}, active={self.active}"


class Conversation(CommonMixin, Base):
    __tablename__ = "conversations"

    user_id: Mapped[uuid.UUID] = mapped_column(
        ForeignKey("users.id", ondelete="cascade"), nullable=False
    )
    clone_id: Mapped[uuid.UUID] = mapped_column(
        ForeignKey("clones.id", ondelete="cascade"), nullable=False
    )
    start_time: Mapped[datetime.datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now()
    )
    end_time: Mapped[datetime.datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        onupdate=func.current_timestamp(),
    )

    user = relationship("User", back_populates="conversations")
    clone = relationship("Clone", back_populates="conversations")
    messages = relationship("Message", back_populates="conversations")


class Message(CommonMixin, Base):
    __tablename__ = "messages"

    conversation_id: Mapped[uuid.UUID] = mapped_column(
        ForeignKey("conversations.id", ondelete="cascade"),
        nullable=False,
    )
    user_id: Mapped[uuid.UUID] = mapped_column(
        ForeignKey("users.id", ondelete="cascade"), nullable=False
    )
    content: Mapped[str] = mapped_column(nullable=False)
    timestamp: Mapped[datetime.datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now()
    )

    user = relationship("User", back_populates="messages")
    conversation = relationship("Conversation", back_populates="messages")


class DocumentCollection(CommonMixin, Base):
    __tablename__ = "document_collections"

    name: Mapped[str] = mapped_column(nullable=False)
    user_id: Mapped[uuid.UUID] = mapped_column(
        ForeignKey("users.id", ondelete="cascade"), nullable=False
    )
    clone_id: Mapped[uuid.UUID] = mapped_column(
        ForeignKey("clones.id", ondelete="cascade"), nullable=False
    )
    vector_db: Mapped[str] = mapped_column(nullable=False)

    user = relationship("User", back_populates="document_collections")
    clone = relationship("Clone", back_populates="document_collections")
    documents = relationship("Document", back_populates="document_collections")


class Document(CommonMixin, Base):
    __tablename__ = "document"

    url: Mapped[str] = mapped_column(nullable=False)
    document_metadata: Mapped[str] = mapped_column(nullable=False)
    document_collection = relationship("DocumentCollection", back_populates="documents")
