# FixMe (Jonny): ASAP try to fix this. It's fucking impossible to properly type the goddamn retrieval functions.
import time
import uuid
from dataclasses import dataclass
from datetime import datetime
from functools import wraps
from typing import Callable, Sequence, TypeVar

import numpy as np
import sqlalchemy as sa
from fastapi import status
from fastapi.exceptions import HTTPException
from opentelemetry import metrics, trace
from sqlalchemy.ext.asyncio import AsyncSession
from typing_extensions import ParamSpec

from app import models
from app.embedding import EmbeddingClient
from app.settings import settings
from clonr.data_structures import Dialogue, Document, Memory, Message, Monologue, Node
from clonr.tokenizer import Tokenizer
from clonr.utils import get_current_datetime

from . import retrieval
from .cache import CloneCache
from .types import MetricType

tracer = trace.get_tracer(__name__)

# TODO (Kevin or Jonny): Run this for all of our query
# methods. Track if it's vsearch, rerank, or gen-agents querying
# get the duration, and number of query characters
meter = metrics.get_meter(settings.BACKEND_APP_NAME)

query_processing_time_meter = meter.create_histogram(
    name="query_processing_time",
    description="Time spent querying",
    unit="s",
)

subroutine_duration = meter.create_histogram(
    name="clonedb_subroutine_duration",
    description="Measures the time spent for each subroutine of clonedb",
)

P = ParamSpec("P")
T = TypeVar("T")


def report_duration(fn: Callable[P, T]):
    @wraps(fn)
    def inner(self, *args: P.args, **kwargs: P.kwargs) -> T:
        attributes = dict(subroutine=fn.__name__)
        start = time.perf_counter()
        result = fn(self, *args, **kwargs)
        duration = time.perf_counter() - start
        subroutine_duration.record(amount=duration, attributes=attributes)
        return result

    return inner


INF = 1_000_000


@dataclass
class QueryNodeResult:
    model: models.Node
    metric: MetricType
    distance: float


@dataclass
class QueryNodeReRankResult:
    model: models.Node
    metric: MetricType
    distance: float
    rerank_score: float


@dataclass
class QueryMonologueResult:
    model: models.Monologue
    metric: MetricType
    distance: float


@dataclass
class QueryMonologueReRankResult:
    model: models.Monologue
    metric: MetricType
    distance: float
    rerank_score: float


@dataclass
class QueryMemoryResult:
    model: models.Memory
    recency_score: float
    relevance_score: float
    importance_score: float
    score: float
    metric: MetricType


def inplace_convert_embeddings_to_hierarchical_weighting(
    nodes: list[Node], weight_decay_factor: float
):
    # If the doc is indexed as a tree, we add in the embeddings of parent
    # elements to better match, as x1 + (1/gamma) * x2 + (1/gamma)^2 * x3 + ...
    # this operates in place!
    if weight_decay_factor > 0:
        _node_dict: dict[uuid.UUID, Node] = {nd.id: nd for nd in nodes}
        # since nodes are weighted using parents, sorting will make sure everything
        # is done in order
        ids = sorted(list(range(len(nodes))), key=lambda i: nodes[i].depth)
        for i in ids:
            nd = nodes[i]
            if nd.parent_id:
                new_nd = nd
                emb = np.array(nd.embedding)
                gamma = weight_decay_factor
                while new_nd.parent_id:
                    new_nd = _node_dict[new_nd.parent_id]
                    emb += gamma * np.array(new_nd.embedding)
                    gamma *= weight_decay_factor
                emb /= np.linalg.norm(emb)
                nd.embedding = emb.flatten().tolist()


class CreatorCloneDB:
    def __init__(
        self,
        db: AsyncSession,
        cache: CloneCache,
        tokenizer: Tokenizer,
        embedding_client: EmbeddingClient,
        clone_id: uuid.UUID,
    ):
        self.embedding_client = embedding_client
        self.db = db
        self.cache = cache
        self.tokenizer = tokenizer
        self.clone_id = clone_id

    @tracer.start_as_current_span("add_document")
    @report_duration
    async def add_document(
        self,
        doc: Document,
        nodes: list[Node],
        hierarchical_weight_decay_factor: float = 0.5,
    ) -> models.Document:
        # don't re-do work if it's already there?
        if await self.db.scalar(
            sa.select(models.Document.hash)
            .where(models.Document.hash == doc.hash)
            .where(models.Document.clone_id == self.clone_id)
        ):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Document with the provided content already exists!",
            )

        # Add embedding stuff. Doc embeddings are just the mean of all node embeddings
        embs = await self.embedding_client.encode_passage(
            [x.content.strip() for x in nodes]
        )
        encoder_name = await self.embedding_client.encoder_name()
        for i, node in enumerate(nodes):
            node.embedding = embs[i]
            node.embedding_model = encoder_name
        arr = np.array([node.embedding for node in nodes]).mean(0)
        if await self.embedding_client.is_normalized():
            arr /= np.linalg.norm(arr)
        doc.embedding = arr.tolist()
        doc.embedding_model = await self.embedding_client.encoder_name()

        if doc.index_type == "tree" and hierarchical_weight_decay_factor > 0:
            inplace_convert_embeddings_to_hierarchical_weighting(
                nodes=node, weight_decay_factor=hierarchical_weight_decay_factor
            )

        # Add together to prevent inconsistency, or out-of-order addition
        doc_model = models.Document(
            id=doc.id,
            content=doc.content,
            hash=doc.hash,
            name=doc.name,
            description=doc.description,
            type=doc.type,
            url=doc.url,
            index_type=doc.index_type,
            max_chunk_size=doc.max_chunk_size,
            chunk_overlap=doc.chunk_overlap,
            text_splitter=doc.text_splitter,
            embedding=doc.embedding,
            embedding_model=doc.embedding_model,
            clone_id=self.clone_id,
        )
        node_models = {
            node.id: models.Node(
                id=node.id,
                index=node.index,
                content=node.content.strip(),
                context=node.context,
                embedding=node.embedding,
                embedding_model=node.embedding_model,
                is_leaf=node.is_leaf,
                depth=node.depth,
                document_id=node.document_id,
                clone_id=self.clone_id,
            )
            for node in nodes
        }

        # this will work for trees where each node has at most one parent!
        for node in nodes:
            if node.parent_id and (parent := node_models.get(node.parent_id)):
                node_models[node.id].parent = parent

        self.db.add(doc_model)
        self.db.add_all(node_models.values())
        await self.db.commit()
        await self.db.refresh(doc_model)
        return doc_model

    @tracer.start_as_current_span("add_dialogues")
    async def add_dialogues(
        self,
        dialogues: list[Dialogue],
    ):
        """Requires that the dialogues have messages inside of them!"""
        embedding_model = await self.embedding_client.encoder_name()
        for dialogue in dialogues:
            # batch encode
            embs = await self.embedding_client.encode_passage(
                [x.content for x in dialogue.messages]
            )

            # update the messages in place
            for m, emb in zip(dialogue.messages, embs):
                m.embedding = emb
                m.embedding_model = embedding_model

            # we compute the dialogue embedding by averaging each of its messages
            # maybe good, maybe bad, fuck if I know.
            arr = np.array(embs).mean(0)
            if await self.embedding_client.is_normalized():
                arr /= np.linalg.norm(arr)
            dialogue.embedding = arr.tolist()
            dialogue.embedding_model = embedding_model

            # Actually add the dialogues now. I haven't checked this since the updates.
            # But since dialogues are a V2 feature, hopefully this shouldn't matter too much.
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

    @tracer.start_as_current_span("add_monologues")
    @report_duration
    async def add_monologues(
        self,
        monologues: list[Monologue],
    ) -> Sequence[models.Monologue]:
        monologue_models: list[models.Monologue] = []
        hashes = [m.hash for m in monologues]
        r = await self.db.execute(
            sa.select(models.Monologue.hash)
            .where(models.Monologue.hash.in_(hashes))
            .where(models.Monologue.clone_id == self.clone_id)
        )
        redundant_hashes = set(list(r.all()))
        monologues = [m for m in monologues if m.hash not in redundant_hashes]
        if not monologues:
            return []
        embeddings = await self.embedding_client.encode_passage(
            [m.content for m in monologues]
        )
        embedding_model = await self.embedding_client.encoder_name()
        for m, emb in zip(monologues, embeddings):
            m1 = models.Monologue(
                id=m.id,
                content=m.content,
                source=m.source,
                embedding=emb,
                embedding_model=embedding_model,
                hash=m.hash,
                clone_id=self.clone_id,
            )
            monologue_models.append(m1)
        self.db.add_all(monologue_models)
        await self.db.commit()
        return monologue_models

    @tracer.start_as_current_span("add_public_memories")
    @report_duration
    async def add_public_memories(
        self,
        memories: list[Memory],
    ) -> Sequence[models.Memory]:
        # batch embed
        embs = await self.embedding_client.encode_passage([x.content for x in memories])
        embedding_model = await self.embedding_client.encoder_name()

        # in-place update
        for m, emb in zip(memories, embs):
            m.embedding = emb
            m.embedding_model = embedding_model

        # add all of the memories
        mem_models: list[models.Memory] = []
        for memory in memories:
            # This is unique to us, memories can be hierarchical (i.e. reflections)
            # and so we must pull all children that they depend on
            children: list[models.Memory] = []
            if memory.child_ids:
                r = await self.db.scalars(
                    sa.select(models.Memory).where(
                        models.Memory.id.in_(tuple(memory.child_ids))
                    )
                )
                children = list(r.all())
            mem = models.Memory(
                content=memory.content,
                embedding=memory.embedding,
                embedding_model=memory.embedding_model,
                timestamp=memory.timestamp,
                last_accessed_at=memory.last_accessed_at,
                importance=memory.importance,
                is_shared=memory.is_shared,
                depth=memory.depth,
                children=children,
                conversation_id=None,
                clone_id=self.clone_id,
            )
            self.db.add(mem)
            mem_models.append(mem)
        # NOTE (Jonny): is it going to be an issue that we don't refresh these?
        await self.db.commit()
        return mem_models

    @tracer.start_as_current_span("delete_document")
    async def delete_document(self, doc: models.Document) -> None:
        await self.db.delete(doc)
        await self.db.commit()
        return None

    @tracer.start_as_current_span("delete_monologue")
    async def delete_monologue(self, monologue: models.Monologue) -> None:
        await self.db.delete(monologue)
        await self.db.commit()
        return None


class CloneDB:
    def __init__(
        self,
        db: AsyncSession,
        cache: CloneCache,
        tokenizer: Tokenizer,
        embedding_client: EmbeddingClient,
        clone_id: uuid.UUID,
        conversation_id: uuid.UUID,
        user_id: uuid.UUID,
    ):
        self.embedding_client = embedding_client
        self.db = db
        self.cache = cache
        self.tokenizer = tokenizer
        self.clone_id = clone_id
        self.conversation_id = conversation_id
        self.user_id = user_id

    @tracer.start_as_current_span("add_document")
    @report_duration
    @classmethod
    async def add_document(
        cls,
        db: AsyncSession,
        embedding_client: EmbeddingClient,
        clone_id: uuid.UUID,
        doc: Document,
        nodes: list[Node],
    ) -> models.Document:
        # don't re-do work if it's already there?
        if await db.scalar(
            sa.select(models.Document.hash)
            .where(models.Document.hash == doc.hash)
            .where(models.Document.clone_id == clone_id)
        ):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Document with the provided content already exists!",
            )

        # Add embedding stuff. Doc embeddings are just the mean of all node embeddings
        embs = await embedding_client.encode_passage([x.content for x in nodes])
        encoder_name = await embedding_client.encoder_name()
        for i, node in enumerate(nodes):
            node.embedding = embs[i]
            node.embedding_model = encoder_name
        arr = np.array([node.embedding for node in nodes]).mean(0)
        if await embedding_client.is_normalized():
            arr /= np.linalg.norm(arr)
        doc.embedding = arr.tolist()
        doc.embedding_model = await embedding_client.encoder_name()

        # Add together to prevent inconsistency, or out-of-order addition
        doc_model = models.Document(
            id=doc.id,
            content=doc.content,
            hash=doc.hash,
            name=doc.name,
            description=doc.description,
            type=doc.type,
            url=doc.url,
            index_type=doc.index_type,
            embedding=doc.embedding,
            embedding_model=doc.embedding_model,
            clone_id=clone_id,
        )
        node_models = {
            node.id: models.Node(
                id=node.id,
                index=node.index,
                content=node.content,
                context=node.context,
                embedding=node.embedding,
                embedding_model=node.embedding_model,
                is_leaf=node.is_leaf,
                depth=node.depth,
                document_id=node.document_id,
                clone_id=clone_id,
            )
            for node in nodes
        }

        # this will work for trees where each node has at most one parent!
        for node in nodes:
            if node.parent_id and (parent := node_models.get(node.parent_id)):
                node_models[node.id].parent = parent

        db.add(doc_model)
        db.add_all(node_models.values())
        await db.commit()
        await db.refresh(doc_model)
        return doc_model

    @tracer.start_as_current_span("add_dialogues")
    @classmethod
    async def add_dialogues(
        cls,
        db: AsyncSession,
        embedding_client: EmbeddingClient,
        clone_id: uuid.UUID,
        dialogues: list[Dialogue],
    ):
        """Requires that the dialogues have messages inside of them!"""
        embedding_model = await embedding_client.encoder_name()
        for dialogue in dialogues:
            # batch encode
            embs = await embedding_client.encode_passage(
                [x.content for x in dialogue.messages]
            )

            # update the messages in place
            for m, emb in zip(dialogue.messages, embs):
                m.embedding = emb
                m.embedding_model = embedding_model

            # we compute the dialogue embedding by averaging each of its messages
            # maybe good, maybe bad, fuck if I know.
            arr = np.array(embs).mean(0)
            if await embedding_client.is_normalized():
                arr /= np.linalg.norm(arr)
            dialogue.embedding = arr.tolist()
            dialogue.embedding_model = embedding_model

            # Actually add the dialogues now. I haven't checked this since the updates.
            # But since dialogues are a V2 feature, hopefully this shouldn't matter too much.
            msgs: list[models.ExampleDialogueMessage] = []
            for m in dialogue.messages:
                if not (x := await db.get(models.ExampleDialogueMessage, m.id)):
                    x = models.ExampleDialogueMessage(
                        index=m.index,
                        content=m.content,
                        sender_name=m.sender_name,
                        is_clone=m.is_clone,
                        embedding=m.embedding,
                        embedding_model=m.embedding_model,
                        dialogue_id=m.dialogue_id,
                        clone_id=clone_id,
                    )
                msgs.append(x)
            dlg = models.ExampleDialogue(
                source=dialogue.source,
                messages=msgs,
                embedding=dialogue.embedding,
                embedding_model=dialogue.embedding_model,
                clone_id=clone_id,
            )

            db.add_all(msgs)
            db.add(dlg)
            await db.commit()

    @tracer.start_as_current_span("add_monologues")
    @report_duration
    @classmethod
    async def add_monologues(
        cls,
        db: AsyncSession,
        embedding_client: EmbeddingClient,
        clone_id: uuid.UUID,
        monologues: list[Monologue],
    ) -> Sequence[models.Monologue]:
        monologue_models: list[models.Monologue] = []
        hashes = [m.hash for m in monologues]
        r = await db.execute(
            sa.select(models.Monologue.hash)
            .where(models.Monologue.hash.in_(hashes))
            .where(models.Monologue.clone_id == clone_id)
        )
        redundant_hashes = set(list(r.all()))
        monologues = [m for m in monologues if m.hash not in redundant_hashes]
        if not monologues:
            return []
        embeddings = await embedding_client.encode_passage(
            [m.content for m in monologues]
        )
        embedding_model = await embedding_client.encoder_name()
        for m, emb in zip(monologues, embeddings):
            m1 = models.Monologue(
                id=m.id,
                content=m.content,
                source=m.source,
                embedding=emb,
                embedding_model=embedding_model,
                hash=m.hash,
                clone_id=clone_id,
            )
            monologue_models.append(m1)
        db.add_all(monologue_models)
        await db.commit()
        return monologue_models

    @tracer.start_as_current_span("add_memories")
    @report_duration
    async def add_memories(self, memories: list[Memory]) -> Sequence[models.Memory]:
        # batch embed
        embs = await self.embedding_client.encode_passage([x.content for x in memories])
        embedding_model = await self.embedding_client.encoder_name()

        # in-place update
        for m, emb in zip(memories, embs):
            m.embedding = emb
            m.embedding_model = embedding_model

        # add all of the memories
        mem_models: list[models.Memory] = []
        for memory in memories:
            # This is unique to us, memories can be hierarchical (i.e. reflections)
            # and so we must pull all children that they depend on
            children: list[models.Memory] = []
            if memory.child_ids:
                r = await self.db.scalars(
                    sa.select(models.Memory).where(
                        models.Memory.id.in_(tuple(memory.child_ids))
                    )
                )
                children = list(list(r.all()))
            mem = models.Memory(
                content=memory.content,
                embedding=memory.embedding,
                embedding_model=memory.embedding_model,
                timestamp=memory.timestamp,
                last_accessed_at=memory.last_accessed_at,
                importance=memory.importance,
                is_shared=memory.is_shared,
                depth=memory.depth,
                children=children,
                conversation_id=self.conversation_id,
                clone_id=self.clone_id,
            )
            self.db.add(mem)
            mem_models.append(mem)
        # NOTE (Jonny): is it going to be an issue that we don't refresh these?
        await self.db.commit()
        return mem_models

    @tracer.start_as_current_span("add_public_memories")
    @report_duration
    @classmethod
    async def add_public_memories(
        cls,
        clone_id: uuid.UUID,
        db: AsyncSession,
        embedding_client: EmbeddingClient,
        memories: list[Memory],
    ) -> Sequence[models.Memory]:
        # batch embed
        embs = await embedding_client.encode_passage([x.content for x in memories])
        embedding_model = await embedding_client.encoder_name()

        # in-place update
        for m, emb in zip(memories, embs):
            m.embedding = emb
            m.embedding_model = embedding_model

        # add all of the memories
        mem_models: list[models.Memory] = []
        for memory in memories:
            # This is unique to us, memories can be hierarchical (i.e. reflections)
            # and so we must pull all children that they depend on
            children: list[models.Memory] = []
            if memory.child_ids:
                r = await db.scalars(
                    sa.select(models.Memory).where(
                        models.Memory.id.in_(tuple(memory.child_ids))
                    )
                )
                children = list(r.all())
            mem = models.Memory(
                content=memory.content,
                embedding=memory.embedding,
                embedding_model=memory.embedding_model,
                timestamp=memory.timestamp,
                last_accessed_at=memory.last_accessed_at,
                importance=memory.importance,
                is_shared=memory.is_shared,
                depth=memory.depth,
                children=children,
                conversation_id=None,
                clone_id=clone_id,
            )
            db.add(mem)
            mem_models.append(mem)
        # NOTE (Jonny): is it going to be an issue that we don't refresh these?
        await db.commit()
        return mem_models

    @tracer.start_as_current_span("add_message")
    async def add_message(
        self, message: Message, msg_to_unset: models.Message | None = None
    ) -> models.Message:
        if self.conversation_id is None:
            raise ValueError("Adding messages requires conversation_id.")
        if self.user_id is None:
            raise ValueError("Adding messages requires user_id.")
        embedding = await self.embedding_client.encode_passage(message.content)
        embedding_model = await self.embedding_client.encoder_name()
        msg = models.Message(
            id=message.id,
            sender_name=message.sender_name,
            content=message.content,
            timestamp=message.timestamp,
            is_clone=message.is_clone,
            is_main=True,  # always true when 1st adding a message
            is_active=True,  # always true when 1st adding a message
            parent_id=message.parent_id,
            clone_id=self.clone_id,
            conversation_id=self.conversation_id,
            user_id=self.user_id,
            embedding=embedding[0],
            embedding_model=embedding_model,
        )
        self.db.add(msg)
        if msg_to_unset is not None:
            msg_to_unset.is_main = False
        await self.db.commit()
        await self.db.refresh(msg)
        return msg

    @tracer.start_as_current_span("add_entity_context_summary")
    async def add_entity_context_summary(
        self,
        content: str,
        entity_name: str,
        timestamp: datetime = get_current_datetime(),
    ) -> models.EntityContextSummary:
        if self.conversation_id is None:
            raise ValueError(
                "Adding entity context summaries requires conversation_id."
            )
        obj = models.EntityContextSummary(
            content=content,
            entity_name=entity_name,
            timestamp=timestamp,
            clone_id=self.clone_id,
            conversation_id=self.conversation_id,
        )
        self.db.add(obj)
        await self.db.commit()
        await self.db.refresh(obj)
        return obj

    @tracer.start_as_current_span("add_agent_summary")
    async def add_agent_summary(
        self, content: str, timestamp: datetime = get_current_datetime()
    ) -> models.AgentSummary:
        if self.conversation_id is None:
            raise ValueError(
                "Adding entity context summaries requires conversation_id."
            )
        obj = models.AgentSummary(
            content=content,
            timestamp=timestamp,
            clone_id=self.clone_id,
            conversation_id=self.conversation_id,
        )
        self.db.add(obj)
        await self.db.commit()
        await self.db.refresh(obj)
        return obj

    @tracer.start_as_current_span("query_nodes")
    @report_duration
    async def query_nodes(
        self, query: str, params: retrieval.VectorSearchParams
    ) -> list[QueryNodeResult]:
        retrieved_nodes = await retrieval.vector_search(  # type: ignore
            query=query,
            model=models.Node,
            params=params,
            db=self.db,
            embedding_client=self.embedding_client,
            tokenizer=self.tokenizer,
            filters=[models.Node.clone_id == self.clone_id],
        )
        return [
            QueryNodeResult(model=x.model, distance=x.distance, metric=x.metric)  # type: ignore
            for x in retrieved_nodes
        ]

    @tracer.start_as_current_span("query_nodes_with_rerank")
    @report_duration
    async def query_nodes_with_rerank(
        self, query: str, params: retrieval.ReRankSearchParams
    ) -> list[QueryNodeReRankResult]:
        retrieved_nodes = await retrieval.rerank_search(  # type: ignore
            query=query,
            model=models.Node,
            params=params,
            db=self.db,
            embedding_client=self.embedding_client,
            tokenizer=self.tokenizer,
            filters=[models.Node.clone_id == self.clone_id],
        )
        return [
            QueryNodeReRankResult(
                model=x.model,  # type: ignore
                distance=x.distance,
                metric=x.metric,
                rerank_score=x.rerank_score,
            )
            for x in retrieved_nodes
        ]

    @tracer.start_as_current_span("query_monologues")
    @report_duration
    async def query_monologues(
        self, query: str, params: retrieval.VectorSearchParams
    ) -> list[QueryMonologueResult]:
        retrieved_monologues = await retrieval.vector_search(  # type: ignore
            query=query,
            model=models.Monologue,
            params=params,
            db=self.db,
            embedding_client=self.embedding_client,
            tokenizer=self.tokenizer,
            filters=[models.Monologue.clone_id == self.clone_id],
        )
        return [
            QueryMonologueResult(model=x.model, distance=x.distance, metric=x.metric)  # type: ignore
            for x in retrieved_monologues
        ]

    @tracer.start_as_current_span("query_monologues_with_rerank")
    @report_duration
    async def query_monologues_with_rerank(
        self, query: str, params: retrieval.ReRankSearchParams
    ) -> list[QueryMonologueReRankResult]:
        retrieved_monologues = await retrieval.rerank_search(  # type: ignore
            query=query,
            model=models.Monologue,
            params=params,
            db=self.db,
            embedding_client=self.embedding_client,
            tokenizer=self.tokenizer,
            filters=[models.Monologue.clone_id == self.clone_id],
        )
        return [
            QueryMonologueReRankResult(
                model=x.model,  # type: ignore
                distance=x.distance,
                metric=x.metric,
                rerank_score=x.rerank_score,
            )
            for x in retrieved_monologues
        ]

    @tracer.start_as_current_span("query_memories")
    @report_duration
    async def query_memories(
        self,
        query: str,
        params: retrieval.GenAgentsSearchParams,
        update_access_date: bool,
    ) -> list[QueryMemoryResult]:
        # We filter to retrieve either private memories for the conversation, or public memories
        # shared across all conversations
        is_public = sa.and_(
            models.Memory.clone_id == self.clone_id, models.Memory.is_shared
        )
        is_private = models.Memory.conversation_id == self.conversation_id

        if self.conversation_id is None:
            # if no conversation_id is provided, only show public memories
            filters = [is_public]

        filters = [sa.or_(is_public, is_private)]

        retrieved_memories = await retrieval.gen_agents_search(  # type: ignore
            query=query,
            model=models.Memory,
            params=params,
            db=self.db,
            embedding_client=self.embedding_client,
            tokenizer=self.tokenizer,
            filters=filters,
        )

        # For memories, we have to update their `last_accessed_at` field each
        # time they are retrieved from the database
        if update_access_date:
            timestamp = get_current_datetime()
            for r in retrieved_memories:
                r.model.last_accessed_at = timestamp
            await self.db.commit()

        memory_results = [
            QueryMemoryResult(
                model=x.model,  # type: ignore
                recency_score=x.recency_score,
                relevance_score=x.relevance_score,
                importance_score=x.importance_score,
                metric=x.metric,
                score=x.score,
            )
            for x in retrieved_memories
        ]

        return memory_results

    # get operations
    @tracer.start_as_current_span("get_messages")
    @report_duration
    async def get_messages(
        self, num_messages: int | None = None, num_tokens: int | None = None
    ) -> Sequence[models.Message]:
        """Returns the recent messages in chronological order, i.e.
        [newest, ..., oldest]"""
        if self.conversation_id is None:
            raise ValueError("Retrieving memories requires conversation_id.")
        if num_messages is None or num_messages < 1:
            num_messages = INF
        if num_tokens is None or num_tokens < 1:
            num_tokens = INF
        q = (
            sa.select(models.Message)
            .where(models.Message.conversation_id == self.conversation_id)
            .where(models.Message.is_main)
            .where(models.Message.is_active)
            .order_by(models.Message.timestamp.desc())
            .limit(num_messages)
        )
        msg_itr = await self.db.scalars(q)

        if num_tokens >= INF:
            return list(msg_itr.all())

        messages: list[models.Message] = []
        for msg in msg_itr:
            # TODO (Jonny): find a way to make sure this is in sync with the templates
            # this should hopefully be an upper bound on how bad it can be. (if we omit timestamps)
            formatted_content = f"[{msg.time_str}] {msg.content}"
            # add 4 tokens per message due to <|im_start|>role\n and \n
            num_tokens -= self.tokenizer.length(formatted_content) + 4
            if num_tokens < 0:
                break
            messages.append(msg)
        return messages

    @tracer.start_as_current_span("get_memories")
    @report_duration
    async def get_memories(
        self, num_messages: int | None = None, num_tokens: int | None = None
    ) -> Sequence[models.Memory]:
        # There is no last_accessed_at update for just getting memories, that only changes
        # when queried as part of a reflection or conversation
        if self.conversation_id is None:
            raise ValueError("Retrieving memories requires conversation_id.")
        if num_messages is None or num_messages < 1:
            num_messages = INF
        if num_tokens is None or num_tokens < 1:
            num_tokens = INF
        q = (
            sa.select(models.Memory)
            .where(models.Memory.conversation_id == self.conversation_id)
            .order_by(models.Memory.timestamp.desc())
            .limit(num_messages)
        )
        mem_itr = await self.db.scalars(q)

        if num_tokens >= INF:
            return list(mem_itr.all())

        memories: list[models.Memory] = []
        for mem in mem_itr:
            num_tokens -= self.tokenizer.length(mem.content)
            if num_tokens < 0:
                break
            memories.append(mem)
        return memories

    @tracer.start_as_current_span("get_monologues")
    @report_duration
    async def get_monologues(
        self, num_messages: int | None = None, num_tokens: int | None = None
    ) -> list[models.Monologue]:
        if num_messages is None or num_messages < 1:
            num_messages = INF
        if num_tokens is None or num_tokens < 1:
            num_tokens = INF
        q = (
            sa.select(models.Monologue)
            .where(models.Monologue.clone_id == self.clone_id)
            .order_by(models.Message.created_at.desc())
            .limit(num_messages)
        )
        monologue_itr = await self.db.scalars(q)

        if num_tokens >= INF:
            return list(monologue_itr.all())

        monologues: list[models.Monologue] = []
        for monologue in monologue_itr:
            dec = self.tokenizer.length(monologue.content)
            num_tokens -= dec
            if num_tokens < 0:
                break
            monologues.append(monologue)
        return monologues

    @tracer.start_as_current_span("get_entity_context_summary")
    @report_duration
    async def get_entity_context_summary(
        self, entity_name: str, n: int = 1
    ) -> Sequence[models.EntityContextSummary]:
        if self.conversation_id is None:
            raise ValueError(
                "Retrieving entity context summary requires conversation_id."
            )
        q = (
            sa.select(models.EntityContextSummary)
            .where(models.EntityContextSummary.conversation_id == self.conversation_id)
            .where(models.EntityContextSummary.entity_name == entity_name)
            .order_by(models.EntityContextSummary.created_at.desc())
            .limit(n)
        )
        summaries = await self.db.scalars(q)
        return summaries.all()

    @tracer.start_as_current_span("get_agent_summary")
    @report_duration
    async def get_agent_summary(self, n: int = 1) -> Sequence[models.AgentSummary]:
        if self.conversation_id is None:
            raise ValueError("Retrieving agent summary requires conversation_id.")
        q = (
            sa.select(models.AgentSummary)
            .where(models.AgentSummary.conversation_id == self.conversation_id)
            .order_by(models.AgentSummary.created_at.desc())
            .limit(n)
        )
        summaries = await self.db.scalars(q)
        return summaries.all()

    @tracer.start_as_current_span("increment_reflection_counter")
    async def increment_reflection_counter(self, importance: int) -> int:
        if self.conversation_id is None:
            raise ValueError(
                "Cannot increment counter without setting conversation id."
            )
        return await self.cache.reflection_counter(
            conversation_id=self.conversation_id
        ).increment(importance=importance)

    @tracer.start_as_current_span("increment_entity_context_counter")
    async def increment_entity_context_counter(self, importance: int) -> int:
        if self.conversation_id is None:
            raise ValueError(
                "Cannot increment counter without setting conversation id."
            )
        return await self.cache.entity_context_counter(
            conversation_id=self.conversation_id
        ).increment(importance=importance)

    @tracer.start_as_current_span("increment_agent_summary_counter")
    async def increment_agent_summary_counter(self, importance: int) -> int:
        if self.conversation_id is None:
            raise ValueError(
                "Cannot increment counter without setting conversation id."
            )
        return await self.cache.agent_summary_counter(
            conversation_id=self.conversation_id
        ).increment(importance=importance)

    @tracer.start_as_current_span("get_reflection_count")
    async def get_reflection_count(self) -> int:
        return await self.cache.reflection_counter(
            conversation_id=self.conversation_id
        ).get()

    @tracer.start_as_current_span("get_entity_context_count")
    async def get_entity_context_count(self) -> int:
        return await self.cache.entity_context_counter(
            conversation_id=self.conversation_id
        ).get()

    @tracer.start_as_current_span("get_agent_summary_count")
    async def get_agent_summary_count(self) -> int:
        return await self.cache.agent_summary_counter(
            conversation_id=self.conversation_id
        ).get()

    @tracer.start_as_current_span("set_reflection_count")
    async def set_reflection_count(self, value: int) -> None:
        return await self.cache.reflection_counter(
            conversation_id=self.conversation_id
        ).set(value=value)

    @tracer.start_as_current_span("set_entity_context_count")
    async def set_entity_context_count(self, value: int) -> None:
        return await self.cache.entity_context_counter(
            conversation_id=self.conversation_id
        ).set(value=value)

    @tracer.start_as_current_span("set_agent_summary_count")
    async def set_agent_summary_count(self, value: int) -> None:
        return await self.cache.agent_summary_counter(
            conversation_id=self.conversation_id
        ).set(value=value)

    async def _get_ancestors(self, model: T, id: uuid.UUID) -> list[T]:
        getter = (
            sa.select(model)
            .where(model.id == id)
            .cte(name="parent_for", recursive=True)
        )
        recursive_part = sa.select(model).where(model.id == getter.c.parent_id)
        with_recursive = getter.union_all(recursive_part)
        join_condition = model.id == with_recursive.c.id
        final_query = sa.select(model).select_from(
            with_recursive.join(model, join_condition)
        )
        r = await self.db.scalars(final_query)
        return list(r.all())

    @tracer.start_as_current_span("get_message_ancestors")
    @report_duration
    async def get_message_ancestors(
        self, message_id: uuid.UUID
    ) -> list[models.Message]:
        return await self._get_ancestors(model=models.Message, id=message_id)

    @tracer.start_as_current_span("get_node_ancestors")
    @report_duration
    async def get_node_ancestors(self, node_id: uuid.UUID) -> list[models.Node]:
        return await self._get_ancestors(model=models.Node, id=node_id)

    # (Jonny): is a flat list the best data structure to return here?
    # maybe like a hierarchical dict would be better?
    async def _get_descendants(self, model: T, id: uuid.UUID) -> list[T]:
        getter = (
            sa.select(model)
            .where(model.id == id)
            .cte(name="children_for", recursive=True)
        )
        recursive_part = sa.select(model).where(model.parent_id == getter.c.id)
        with_recursive = getter.union_all(recursive_part)
        join_condition = model.id == with_recursive.c.id
        final_query = sa.select(model).select_from(
            with_recursive.join(model, join_condition)
        )
        r = await self.db.scalars(final_query)
        return list(r.all())

    @tracer.start_as_current_span("get_message_descendants")
    @report_duration
    async def get_message_descendants(
        self, message_id: uuid.UUID
    ) -> list[models.Message]:
        return await self._get_descendants(model=models.Message, id=message_id)
