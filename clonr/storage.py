import datetime
import json
import uuid
from pathlib import Path

import numpy as np
import sqlalchemy as sa
from scipy.spatial.distance import cdist
from sqlalchemy.orm import (
    Mapped,
    declarative_base,
    mapped_column,
    relationship,
    sessionmaker,
)

from clonr.data.data_structures import Document as DocumentStruct
from clonr.data.data_structures import Node as NodeStruct
from clonr.embedding import CrossEncoder, EmbeddingModel

Base = declarative_base()


class InMemoryVectorDB:
    def __init__(
        self,
        encoder: EmbeddingModel = EmbeddingModel.default(),
        cross_encoder: CrossEncoder = CrossEncoder.default(),
        k_biencoder: int = 10,
    ):
        self.encoder = encoder
        self.cross_encoder = cross_encoder
        self.dimension = encoder.dimension
        self._vectors = np.empty((1 << 10, self.dimension))
        self._metadata = {}
        self._id_to_index = {}
        self._index_to_id = {}
        self._size = 0
        self._k_biencoder = k_biencoder

    def save_to_disk(self):
        path = Path(__file__).parent / ".vectordb"
        if not path.exists or not path.is_dir():
            path.mkdir()
        with open(path / "metatdata.json", "w") as f:
            json.dump(f, self._metadata)
        with open(path / "id_to_index.json", "w") as f:
            json.dump(f, self._id_to_index)
        np.save(path / "vectors", self._vectors)

    @classmethod
    def from_disk(cls):
        path = Path(__file__).parent / ".vectordb"
        obj = cls()
        with open(path / "metatdata.json", "w") as f:
            obj._metadata = json.load(f)
        with open(path / "id_to_index.json", "w") as f:
            obj._id_to_index = json.load(f)
            obj._index_to_id = {v: k for k, v in obj._id_to_index.items()}
        obj._vectors = np.load(path / "vectors")
        obj._size = len(obj._metadata)
        return obj

    @property
    def size(self):
        return self._size

    def _grow(self):
        N = len(self._vectors)
        _vectors = np.empty((2 * N, self.dimension))
        _vectors[:N] = self._vectors
        self._vectors = _vectors

    def add(self, node: NodeStruct):
        if node.id in self._metadata:
            raise ValueError("ID ({node.id}) already exists!")
        if node.embedding is None:
            node.embedding = self.encoder.encode_passage([node.content])[0]
            node.embedding_model = self.encoder.name
        data = node.dict()
        embedding = data.pop("embedding")
        if self._size >= len(self._vectors):
            self._grow()
        self._vectors[self._size] = embedding
        self._metadata[self._size] = data
        self._index_to_id[self._size] = node.id
        self._id_to_index[id] = self._size
        self._size += 1

    def add_all(self, nodes: list[NodeStruct]):
        embeddings = self.encoder.encode_passage([node.content for node in nodes])
        for e, node in zip(embeddings, nodes):
            node.embedding = e
            node.embedding_model = self.encoder.name
            self.add(node)

    def delete(self, id: str):
        if id in self._id_to_index:
            index = self._id_to_index[id]
            self._size -= 1
            self._vectors[index] = self._vectors[self._size]
            self._metadata[index] = self._metadata.pop(self._size)
            self._index_to_id[index] = self._index_to_id.pop(self._size)
            self._id_to_index[self._index_to_id[index]] = index
            return id

    def query(self, query: str, k: int = 3) -> list[dict]:
        k_biencoder = 2 * k if k > self._k_biencoder else self._k_biencoder
        q = np.array(self.encoder.encode_query(query))
        dists = cdist(q, self._vectors[: self._size], metric="cosine")[0]
        top_ids = np.argsort(dists)[:k_biencoder]
        res: list[dict] = []
        for i in top_ids:
            cur = self._metadata[i].copy()
            cur["similarity_score"] = 1 - dists[i]
            res.append(cur)
        scores = self.cross_encoder.similarity_score(
            query, [x["content"].strip() for x in res]
        )
        top_ids = np.argsort([-x[0] for x in scores])
        return [{**res[i], "rerank_score": scores[i][0]} for i in top_ids[:k]]


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


# class AuthenticatedDB:
#     def __init__(self):
#         self.session = SessionLocal
#         self.vectorDB = vectorDB

#     def add_document(self, document: DocumentStruct):
#         with self.session() as db:
#             doc = Document(**document.dict(exclude={'n_chars'}))
#             db.add(doc)
#             db.commit()
#             db.flush(doc)
#         return doc

#     def add_node(self)
