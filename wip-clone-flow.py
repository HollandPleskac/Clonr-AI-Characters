import os

import sqlalchemy as sa

cwd = os.getcwd()
os.chdir("backend")
os.environ["POSTGRES_HOST"] = "localhost"
from app import models
from app.db.cache import _redis_connection
from app.db.db import (
    async_session_maker,
    clear_db,
    create_superuser,
    init_db,
    wait_for_db,
)
from app.settings import settings
from fastapi.encoders import jsonable_encoder
from fastapi_users.password import PasswordHelper

os.chdir(cwd)

from clonr.data.load_examples import (
    load_makima_data,
    load_makima_example_dialogues,
    load_makima_greeting_message,
    load_makima_long_description,
    load_makima_short_description,
)


async def create_superuser():
    async with async_session_maker() as db:
        password = settings.SUPERUSER_PASSWORD
        hashed_password = PasswordHelper().hash(password=password)
        user = models.User(
            email=settings.SUPERUSER_EMAIL,
            is_superuser=True,
            hashed_password=hashed_password,
        )
        db.add(user)
        try:
            await db.commit()
        except:
            await db.rollback()
            raise
    return user


async def create_clone_model(user):
    async with async_session_maker() as db:
        clone_model = models.Clone(
            name="Makima",
            short_description=load_makima_short_description(),
            long_description=load_makima_long_description(),
            greeting_message=load_makima_greeting_message(),
            user=user,
        )
        db.add(clone_model)
        await db.commit()
        await db.flush(clone_model)
    return clone_model


# # Run for cell 1
# await wait_for_db()
# await init_db()
# await clear_db()
# await init_db()
# user = await create_superuser()
# clone_model = await create_clone_model(user)
# async with async_session_maker() as db:
#     clone_model = await db.get(models.Clone, clone_model.id)


import enum
import uuid
from collections import Counter
from dataclasses import dataclass
from typing import Protocol, TypeVar

import numpy as np
from loguru import logger
from pydantic import BaseModel, Field, root_validator
from sqlalchemy.ext.asyncio import AsyncSession

from clonr import templates
from clonr.data.parsers import (
    BasicWebParser,
    ParserException,
    WikipediaParser,
    YoutubeTranscriptParser,
    url_to_doc,
)
from clonr.data_structures import (
    Dialogue,
    DialogueMessage,
    Document,
    Memory,
    Message,
    Node,
)
from clonr.embedding import CrossEncoder, EmbeddingModel
from clonr.index import Index, ListIndex, TreeIndex
from clonr.llms import LLM, GenerationParams, LlamaCpp, MockLLM, OpenAI, OpenAIModelEnum
from clonr.text_splitters import SentenceSplitter, TextSplitter, TokenSplitter
from clonr.tokenizer import Tokenizer

INF = int(1e10)


class VectorSearchProtocol(Protocol):
    embedding: list[float] | np.ndarray
    content: str


VectorSearchable = TypeVar("VectorSearchable", bound=VectorSearchProtocol)


class MetricType(str, enum.Enum):
    """Distance metrics available.
    Quick distance math because I'm stupid.
    cosine similarity = $\cos\theta = (a \cdot b) / |a||b|$. So the range is -1 for anticorrelated and +1 for correlated.
    inner product = $a \cdot b$ which is equivalent to cosine similarity for normalized vectors
    cosine distance is not a real distance (triangle inequality violated). Given by 1 - cossim and range is [0, 2]
    GenAgents normalizes to [0, 1] which is equivalent to dividing by 2.

    Pgvector only supports three types, cosine, inner_product, and euclidean.
    https://github.com/pgvector/pgvector-python/blob/master/pgvector/sqlalchemy/__init__.py
    """

    cosine: str = "cosine"
    inner_product: str = "inner_product"
    euclidean: str = "euclidean"


@dataclass
class VectorSearchResult:
    model: VectorSearchable
    distance: float
    metric: MetricType


@dataclass
class ReRankResult(VectorSearchResult):
    rerank_score: float


class VectorSearchParams(BaseModel):
    max_items: int = Field(
        default=INF, ge=1, detail="Maximum number of items to retrieve from query"
    )
    max_tokens: int = Field(
        default=INF,
        ge=16,
        detail="Maximum number of tokens from all retrieved results, inlcuding newlines",
    )
    metric: MetricType = Field(
        default=MetricType.cosine,
        detail="Which metric to use. Inner product is faster, and equal to cosine if all embeddings are normalized (which they should be for us).",
    )


class CloneDB:
    def __init__(
        self,
        db: AsyncSession,
        encoder: EmbeddingModel,  # Best to have this tightly connected to DB!
        tokenizer: Tokenizer,
        clone_id: str | uuid.UUID,
        conversation_id: str | uuid.UUID | None = None,
        cross_encoder: CrossEncoder | None = None,
    ):
        self.db = db
        self.encoder = encoder
        self.cross_encoder = cross_encoder
        self.tokenizer = tokenizer
        self._clone_id = clone_id
        self._conversation_id = conversation_id

    @property
    def clone_id(self):
        return self._clone_id

    @property
    def conversation_id(self):
        return self._conversation_id

    async def get_clone_model(self) -> models.Clone:
        return await self.db.get(models.Clone, self.clone_id)

    async def get_conversation_model(self):
        return await self.db.get(models.Conversation, self.conversation_id)

    async def get_document_by_hash(self, hash: str):
        return await self.db.scalar(
            sa.select(models.Document).where(models.Document.hash == hash)
        )

    async def get_dialogue_by_hash(self, hash: str):
        return await self.db.scalar(
            sa.select(models.ExampleDialogue).where(models.ExampleDialogue.hash == hash)
        )

    async def add_document_and_nodes(self, doc: Document, nodes: list[Node]):
        # don't re-do work if it's already there?
        if await self.get_document_by_hash(hash=doc.hash):
            return

        # Add embedding stuff. Doc embeddings are just the mean of all node embeddings
        embs = self.encoder.encode_passage([x.content for x in nodes])
        for i, node in enumerate(nodes):
            node.embedding = embs[i]
            node.embedding_model = self.encoder.name
        doc.embedding = np.array([node.embedding for node in nodes]).mean(0).tolist()
        if self.encoder.normalized:
            doc.embedding /= np.linalg.norm(doc.embedding)
        doc.embedding_model = self.encoder.name

        # Add together to prevent inconsistency, or out-of-order addition
        doc_model = models.Document(
            id=doc.id,
            name=doc.name,
            content=doc.content,
            hash=doc.hash,
            description=doc.description,
            url=doc.url,
            index_type=doc.index_type,
            clone_id=self.clone_id,
            embedding=doc.embedding,
            embedding_model=doc.embedding_model,
        )
        node_models = {
            node.id: models.Node(
                id=node.id,
                index=node.index,
                content=node.content,
                context=node.context,
                is_leaf=node.is_leaf,
                depth=node.depth,
                embedding=node.embedding,
                embedding_model=node.embedding_model,
                document_id=node.document_id,
                clone_id=self.clone_id,
            )
            for node in nodes
        }

        # this will work for trees where each node has at most one parent!
        for node in nodes:
            node_models[node.id].parent = node_models.get(node.parent_id)

        self.db.add(doc_model)
        self.db.add_all(node_models.values())
        await self.db.commit()

    async def add_dialogue(self, dialogue: Dialogue):
        for x in dialogue.messages:
            x.embedding = self.encoder.encode_passage(x.content)[0]
            x.embedding_model = self.encoder.name
        dialogue.embedding = (
            np.array([x.embedding for x in dialogue.messages]).mean(0).tolist()
        )
        if self.encoder.normalized:
            dialogue.embedding /= np.linalg.norm(dialogue.embedding)
        dialogue.embedding_model = self.encoder.name

        msgs: list[models.ExampleDialogueMessage] = []
        for m in dialogue.messages:
            if not (x := await self.db.get(models.ExampleDialogueMessage, m.id)):
                x = models.ExampleDialogueMessage(
                    index=m.index,
                    content=m.content,
                    sender_name=m.sender_name,
                    is_clone=m.is_clone,
                    embedding=m.embedding,
                    embedding_model=m.embedding_model,
                    dialogue_id=m.dialogue_id,
                    clone_id=self.clone_id,
                )
            msgs.append(x)
        dlg = models.ExampleDialogue(
            source=dialogue.source,
            messages=msgs,
            embedding=dialogue.embedding,
            embedding_model=dialogue.embedding_model,
            clone_id=self.clone_id,
        )

        self.db.add_all(msgs)
        self.db.add(dlg)
        await self.db.commit()

    async def delete_document(self, document_id: str | uuid.UUID):
        if doc := await self.db.get(models.Document, document_id):
            self.db.delete(doc)
            await self.db.commit()

    async def delete_dialogue(self, document_id: str | uuid.UUID):
        if doc := await self.db.get(models.Dialogue, document_id):
            self.db.delete(doc)
            await self.db.commit()

    async def _vector_search(
        self,
        query: str,
        model: VectorSearchable,
        params: VectorSearchParams,
        filters: list[sa.SQLColumnExpression] | None = None,
    ) -> list[VectorSearchResult]:
        q = self.encoder.encode_query(query)[0]
        if params.metric == MetricType.cosine:
            dist = model.embedding.cosine_distance(q)
        elif params.metric == MetricType.euclidean:
            dist = -model.embedding.l2_distance(q)
        elif params.metric == MetricType.inner_product:
            assert (
                self.encoder.normalized
            ), "Cannot user inner product with non-normalized embeddings."
            # NOTE (Jonny): I have no fucking idea why, but max_inner_product is actually the negative of A \cdot B
            # cosine distance in pgvector is correctly 1 - A \cdot B, so here we have to do 1 + to match it.
            dist = 1 + model.embedding.max_inner_product(q)
        else:
            raise TypeError(f"Invalid distance type: ({params.metric})")
        dist = dist.label("distance")

        # Order by should be ascending, as we want to minimize distance here
        stmt = sa.select(model, dist)
        for f in filters or []:
            stmt = stmt.where(f)
        stmt = stmt.order_by(dist.asc()).limit(params.max_items)
        r = await db.execute(stmt)

        res: list[VectorSearchResult] = []
        max_tokens = (
            params.max_tokens
        )  # copy so we don't mess up when using shared params.
        for i, (mdl, scr) in enumerate(r):
            if i >= params.max_items:
                break
            max_tokens -= self.tokenizer.length(mdl.content)
            if max_tokens >= 0:
                cur = VectorSearchResult(model=mdl, distance=scr, metric=params.metric)
                res.append(cur)
        return res

    def _rerank(
        self, query: str, results: list[VectorSearchResult]
    ) -> list[ReRankResult]:
        if self.cross_encoder is None:
            raise ValueError(
                "If using re-rank retrieval, you must pass a cross-encoder to the constructor."
            )
        if not results:
            return []
        passages = [x.model.content for x in results]
        rerank_scores = self.cross_encoder.similarity_score(
            query=query, passages=passages
        )
        res = [
            ReRankResult(
                model=m.model, distance=m.distance, metric=m.metric, rerank_score=scr
            )
            for m, scr in zip(results, rerank_scores)
        ]
        # We want to maximize the ReRank score! It's a similarity measure which can
        # be normalized with a sigmoid
        res.sort(key=lambda x: (-x.rerank_score, x.distance))
        return res

    async def add_memory(self, memory: Memory):
        embedding = self.encoder.encode_passage(memory.content)[0]
        r = await self.db.scalars(
            sa.select(models.Memory).where(
                models.Memory.id.in_(tuple(memory.child_ids))
            )
        )
        children = r.all()
        mem = models.Memory(
            content=memory.content,
            embedding=embedding,
            embedding_model=self.encoder.name,
            timestamp=memory.timestamp,
            last_accessed_at=memory.last_accessed_at,
            importance=memory.importance,
            is_shared=self.conversation_id is None,
            depth=memory.depth,
            children=children,
            conversation_id=self.conversation_id,
            clone_id=self.clone_id,
        )
        self.db.add(mem)
        await self.db.commit()

    async def query_nodes(
        self, query: str, params: VectorSearchParams, rerank: bool = True
    ) -> list[VectorSearchResult] | list[ReRankResult]:
        filters = [models.Node.clone_id == self.clone_id]
        results = await self._vector_search(
            query=query, model=models.Node, params=params, filters=filters
        )
        if rerank:
            results = self._rerank(query=query, results=results)
        return results

    async def query_dialogues(
        self, query: str, params: VectorSearchParams, rerank: bool = False
    ) -> list[VectorSearchResult] | list[ReRankResult]:
        filters = [
            models.ExampleDialogueMessage.clone_id == self.clone_id,
            models.ExampleDialogueMessage.is_clone == True,
            models.Example,
        ]
        results = await self._vector_search(
            query=query,
            model=models.ExampleDialogueMessage,
            params=params,
            filters=filters,
        )
        if rerank:
            results = self._rerank(query=query, results=results)
        return results


# # Run for cell 2
# from clonr.llms.callbacks import LoggingCallback

# tokenizer = Tokenizer.from_openai('gpt-3.5-turbo')
# splitter = SentenceSplitter(tokenizer=tokenizer, use_tokens=True)
# encoder = EmbeddingModel.default()
# cross_encoder = CrossEncoder.default()
# llm = MockLLM('fuck you pay me ' * 100, callbacks=[LoggingCallback()])

# statements = ["I like ice cream.", 'I like cookies.', "I don't like curry", "I like candy.", "I run an ice cream shop."]
# seed_memories = [Memory(content=s, importance=3) for s in statements]
# wiki_text = load_makima_data()
# example_dialogues = load_makima_example_dialogues()

# clonedb = CloneDB(
#     db=db,
#     encoder=encoder,
#     cross_encoder=cross_encoder,
#     tokenizer=tokenizer,
#     clone_id=clone_model.id,
# )

# # Add indexed document
# index = TreeIndex(tokenizer=tokenizer, splitter=splitter, llm=llm)
# doc = Document(content=wiki_text)
# nodes = await index.abuild(doc=doc)
# logger.info(f"Add Document ({doc.id}) to DB")
# await clonedb.add_document_and_nodes(doc=doc, nodes=nodes)

# # Add dialogues
# for d in example_dialogues:
#     logger.info(f"Add Dialogue ({d.id}) to DB")
#     await clonedb.add_dialogue(d)

# # Add seed memories
# for m in seed_memories:
#     logger.info(f"Add Memory ({m.id}) to DB")
#     await clonedb.add_memory(m)
