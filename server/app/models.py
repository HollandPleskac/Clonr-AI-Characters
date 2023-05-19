import datetime
import uuid

from sqlalchemy import DateTime, ForeignKey, func, text
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column


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


""" 
Scaffolding. delete all of the code below this later.
"""


class ElevenClone(CommonMixin, Base):
    __tablename__ = "eleven_clones"

    clone_id: Mapped[str] = mapped_column(unique=True, nullable=False)
    active: Mapped[bool] = mapped_column(default=False)
    min_training_audio: Mapped[float]
    audio_bucket: Mapped[str] = mapped_column(nullable=False)
    user_id: Mapped[uuid.UUID] = mapped_column(
        ForeignKey("users.id", ondelete="cascade"), nullable=False
    )

    def __repr__(self):
        return f"ElevenClone(clone_id={self.email}, registered={self.registered}"


class User(CommonMixin, Base):
    __tablename__ = "users"

    email: Mapped[str] = mapped_column(unique=True, nullable=False)
    active: Mapped[bool] = mapped_column(default=True)
    is_superuser: Mapped[bool] = mapped_column(default=False)

    def __repr__(self):
        return f"User(email={self.email}, registered={self.registered}"
