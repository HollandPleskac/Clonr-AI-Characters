import datetime
import uuid

import sqlalchemy as sa
from sqlalchemy.orm import (
    Mapped,
    declarative_base,
    mapped_column,
    relationship,
    sessionmaker,
)

Base = declarative_base()


class CommonMixin:
    id: Mapped[uuid.UUID] = mapped_column(primary_key=True, default=uuid.uuid4)
    created_at: Mapped[datetime.datetime] = mapped_column(
        sa.DateTime(timezone=True), server_default=sa.func.now()
    )
    updated_at: Mapped[datetime.datetime] = mapped_column(
        sa.DateTime(timezone=True),
        server_default=sa.func.now(),
        onupdate=sa.func.current_timestamp(),
    )


class Document(CommonMixin, Base):
    __tablename__ = "documents"

    content: Mapped[str]
    embedding_model: Mapped[str] = mapped_column(nullable=True)
    nodes: Mapped[list["Node"]] = relationship(
        "Node", back_populates="document", cascade="all, delete-orphan"
    )

    def __eq__(self, other):
        return self.id == other.id

    def __repr__(self):
        name = self.__class__.__name__
        content = self.content
        n = 20
        msg = f"... + {len(content) - n} chars"
        if len(content) > n + len(msg):
            content = content[:n] + msg
        return f"{name}Model(id={str(self.id)}, content={content})"


node_to_node = sa.Table(
    "node_to_node",
    Base.metadata,
    sa.Column("parent_id", sa.Uuid, sa.ForeignKey("nodes.id"), primary_key=True),
    sa.Column("child_id", sa.Uuid, sa.ForeignKey("nodes.id"), primary_key=True),
)


class Node(CommonMixin, Base):
    __tablename__ = "nodes"

    index: Mapped[int]
    is_leaf: Mapped[bool]
    content: Mapped[str]
    context: Mapped[str] = mapped_column(nullable=True)
    embedding_model: Mapped[str]
    document_id: Mapped[uuid.UUID] = mapped_column(sa.ForeignKey("documents.id"))
    document: Mapped["Document"] = relationship("Document", back_populates="nodes")
    parent_id: Mapped[uuid.UUID] = mapped_column(
        sa.ForeignKey("nodes.id"), nullable=True
    )
    parent: Mapped["Node"] = relationship(
        "Node", back_populates="children", remote_side="Node.id"
    )
    children: Mapped[list["Node"]] = relationship("Node", back_populates="parent")

    def __eq__(self, other):
        return self.id == other.id

    def __repr__(self):
        name = self.__class__.__name__
        content = self.content
        n = 20
        msg = f"... + {len(content) - n} chars"
        if len(content) > n + len(msg):
            content = content[:n] + msg
        return (
            f"{name}Model(id={str(self.id)}, index={self.index}, " f"content={content})"
        )


def get_sessionmaker(path: str = "sqlite:///"):
    engine = sa.create_engine(path)
    Base.metadata.create_all(bind=engine)
    SessionLocal = sessionmaker(engine, expire_on_commit=False, autoflush=False)
    return SessionLocal
