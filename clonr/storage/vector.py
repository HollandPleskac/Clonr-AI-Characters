import datetime
import json
from pathlib import Path

import numpy as np
from scipy.spatial.distance import cdist

from clonr.data_structures import Node
from clonr.embedding import CrossEncoder, EmbeddingModel


class InMemoryVectorDB:
    def __init__(
        self,
        encoder: EmbeddingModel = EmbeddingModel.default(),
        cross_encoder: CrossEncoder = CrossEncoder.default(),
    ):
        self.encoder = encoder
        self.cross_encoder = cross_encoder
        self.dimension = encoder.dimension
        self._vectors = np.empty((1 << 10, self.dimension))
        self._metadata = {}
        self._id_to_index = {}
        self._index_to_id = {}
        self._size = 0

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

    # TODO (Jonny): the typing is wrong here, it should really by anything that has
    # a embedding, content attributes. Not sure how to do that in Python
    def add(self, node: Node):
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

    # TODO (Jonny): the typing is wrong here, it should really by anything that has
    # an embedding attribute. Not sure how to do that in Python
    def add_all(self, nodes: list[Node]):
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

    def delete_all(self, ids: list[str]):
        for id in ids:
            self.delete(id)

    def query(self, query: str | list[str], k: int = 10) -> list[dict]:
        if k < 1:
            k = 1_000_000
        if isinstance(query, list):
            ids = set([])
            res = [x for y in query for x in self.query(y, k)]
            new_res = []
            for x in res:
                if x["id"] not in ids:
                    ids.add(x["id"])
                    new_res.append(x)
            new_res.sort(key=lambda x: -x["similarity_score"])
            return new_res[:k]
        q = np.array(self.encoder.encode_query(query))
        dists = cdist(q, self._vectors[: self._size], metric="cosine")[0]
        top_ids = np.argsort(dists)[:k]
        res: list[dict] = []
        for i in top_ids:
            cur = self._metadata[i].copy()
            cur["similarity_score"] = 1 - dists[i]
            res.append(cur)
        return res
