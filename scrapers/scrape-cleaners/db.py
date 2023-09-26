from typing import Optional
import sqlalchemy as sa
from sqlalchemy.engine import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, relationship


class Base(DeclarativeBase):
    pass


clones_to_tags = sa.Table(
    "clones_to_tags",
    Base.metadata,
    sa.Column("tag_id", sa.Integer, sa.ForeignKey("tags.id"), primary_key=True),
    sa.Column("clone_id", sa.Integer, sa.ForeignKey("clones.id"), primary_key=True),
)

clones_to_images = sa.Table(
    "clones_to_images",
    Base.metadata,
    sa.Column("image_id", sa.Integer, sa.ForeignKey("images.id"), primary_key=True),
    sa.Column("clone_id", sa.Integer, sa.ForeignKey("clones.id"), primary_key=True),
)

clones_to_documents = sa.Table(
    "clones_to_documents",
    Base.metadata,
    sa.Column(
        "document_id", sa.Integer, sa.ForeignKey("documents.id"), primary_key=True
    ),
    sa.Column("clone_id", sa.Integer, sa.ForeignKey("clones.id"), primary_key=True),
)


class ImageModel(Base):
    __tablename__ = "images"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    url: Mapped[str] = mapped_column(unique=True, index=True)
    source: Mapped[str]
    content: Mapped[bytes]
    format: Mapped[str]
    clones: Mapped[list["Clone"]] = relationship(
        secondary=clones_to_images, back_populates="images"
    )


class Tag(Base):
    __tablename__ = "tags"

    id: Mapped[int] = mapped_column(autoincrement=True, primary_key=True)
    name: Mapped[str] = mapped_column(unique=True)
    clones: Mapped[list["Clone"]] = relationship(
        secondary=clones_to_tags, back_populates="tags"
    )


class Document(Base):
    __tablename__ = "documents"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    content: Mapped[str]
    name: Mapped[str]
    description: Mapped[Optional[str]] = mapped_column(default=None)
    type: Mapped[Optional[str]] = mapped_column(default=None)
    url: Mapped[Optional[str]] = mapped_column(default=None, unique=True)
    clones: Mapped[list["Clone"]] = relationship(
        secondary=clones_to_documents, back_populates="documents"
    )


class Clone(Base):
    __tablename__ = "clones"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    name: Mapped[str]
    short_description: Mapped[str]
    long_description: Mapped[str]
    greeting: Mapped[str]
    example_dialogues: Mapped[str] = mapped_column(nullable=True)
    avatar_uri: Mapped[str] = mapped_column(nullable=True)
    scenario: Mapped[str] = mapped_column(nullable=True)
    scrape_source: Mapped[str]
    creator: Mapped[str] = mapped_column(nullable=True)
    num_messages: Mapped[int] = mapped_column(nullable=True)
    num_conversations: Mapped[int] = mapped_column(nullable=True)
    _metadata: Mapped[str] = mapped_column(nullable=True)
    doc_links: Mapped[str]
    expanded_links: Mapped[str]
    final_links: Mapped[str]
    tags: Mapped[list["Tag"]] = relationship(
        secondary=clones_to_tags, back_populates="clones", lazy="joined"
    )
    images: Mapped[list["ImageModel"]] = relationship(
        secondary=clones_to_images, back_populates="clones", lazy="joined"
    )
    documents: Mapped[list["Document"]] = relationship(
        secondary=clones_to_documents, back_populates="clones", lazy="joined"
    )


DATABASE_URL = "sqlite:///launch-clones.sqlite"
engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(engine, expire_on_commit=False, autoflush=False)  # type: ignore
