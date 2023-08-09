import uuid
from datetime import datetime

import numpy as np
import sqlalchemy as sa
from sqlalchemy.ext.asyncio import AsyncSession

from app import models
from app.embedding import EmbeddingClient
from clonr.data_structures import Dialogue, Document, Memory, Message, Monologue, Node
from clonr.tokenizer import Tokenizer
from clonr.utils import get_current_datetime

from . import retrieval
from .cache import CloneCache

INF = 1_000_000


class QueryNodeResult(retrieval.VectorSearchResult):
    model: models.Node


class QueryNodeReRankResult(retrieval.ReRankResult):
    model: models.Node


class QueryMonologueResult(retrieval.VectorSearchResult):
    model: models.Monologue


class QueryMonologueReRankResult(retrieval.ReRankResult):
    model: models.Monologue


class QueryMemoryResult(retrieval.GenAgentsSearchResult):
    model: models.Memory


class CloneDB:
    def __init__(
        self,
        db: AsyncSession,
        cache: CloneCache,
        tokenizer: Tokenizer,
        embedding_client: EmbeddingClient,
        clone_id: str | uuid.UUID,
        conversation_id: str | uuid.UUID,
    ):
        self.embedding_client = embedding_client
        self.db = db
        self.cache = cache
        self.tokenizer = tokenizer
        self.clone_id = clone_id
        self.conversation_id = conversation_id

    async def add_document(self, doc: Document, nodes: list[Node]) -> models.Document:
        # don't re-do work if it's already there?
        if await self.db.scalar(
            sa.select(models.Document.hash).where(models.Document.hash == doc.hash)
        ):
            return

        # Add embedding stuff. Doc embeddings are just the mean of all node embeddings
        embs = await self.embedding_client.encode_passage([x.content for x in nodes])
        encoder_name = await self.embedding_client.encoder_name()
        for i, node in enumerate(nodes):
            node.embedding = embs[i]
            node.embedding_model = encoder_name
        doc.embedding = np.array([node.embedding for node in nodes]).mean(0).tolist()
        if await self.embedding_client.is_normalized():
            doc.embedding /= np.linalg.norm(doc.embedding)
        doc.embedding_model = await self.embedding_client.encoder_name()

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
            clone_id=self.clone_id,
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
        await self.db.refresh(doc_model)
        return doc_model

    async def add_dialogues(self, dialogues: list[Dialogue]):
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
            dialogue.embedding = np.array(embs).mean(0).tolist()
            if await self.embedding_client.is_normalized():
                dialogue.embedding /= np.linalg.norm(dialogue.embedding)
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

    async def add_monologues(
        self, monologues: list[Monologue]
    ) -> list[models.Monologue]:
        monologue_models: list[models.Monologue] = []
        hashes = [m.hash for m in monologues]
        r = await self.db.execute(
            sa.select(models.Monologue.hash).where(models.Monologue.hash.in_(hashes))
        )
        redundant_hashes = set(r.all())
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

    async def add_memories(self, memories: list[Memory]) -> list[models.Memory]:
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
                children = r.all()
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

    async def add_message(self, message: Message) -> models.Message:
        if self.conversation_id is None:
            raise ValueError("Adding messages requires conversation_id.")
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
        )
        self.db.add(msg)
        await self.db.commit()
        await self.db.refresh(msg)
        return msg

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

    async def query_nodes(
        self, query: str, params: retrieval.VectorSearchParams
    ) -> list[QueryNodeResult]:
        return await retrieval.vector_search(
            query=query,
            model=models.Node,
            params=params,
            db=self.db,
            embedding_client=self.embedding_client,
            tokenizer=self.tokenizer,
            filters=[models.Node.clone_id == self.clone_id],
        )

    async def query_nodes_with_rerank(
        self, query: str, params: retrieval.ReRankSearchParams
    ) -> list[QueryNodeReRankResult]:
        return await retrieval.rerank_search(
            query=query,
            model=models.Node,
            params=params,
            db=self.db,
            embedding_client=self.embedding_client,
            tokenizer=self.tokenizer,
            filters=[models.Node.clone_id == self.clone_id],
        )

    async def query_monologues(
        self, query: str, params: retrieval.VectorSearchParams
    ) -> list[QueryMonologueResult]:
        return await retrieval.vector_search(
            query=query,
            model=models.Monologue,
            params=params,
            db=self.db,
            embedding_client=self.embedding_client,
            tokenizer=self.tokenizer,
            filters=[models.Monologue.clone_id == self.clone_id],
        )

    async def query_monologues_with_rerank(
        self, query: str, params: retrieval.ReRankSearchParams
    ) -> list[QueryMonologueReRankResult]:
        return await retrieval.rerank_search(
            query=query,
            model=models.Monologue,
            params=params,
            db=self.db,
            embedding_client=self.embedding_client,
            tokenizer=self.tokenizer,
            filters=[models.Monologue.clone_id == self.clone_id],
        )

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

        memory_results = await retrieval.gen_agents_search(
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
            for r in memory_results:
                r.model.last_accessed_at = timestamp
                self.db.add(r.model)
            await self.db.commit()

        return memory_results

    # get operations
    async def get_messages(
        self, num_messages: int | None = None, num_tokens: int | None = None
    ) -> list[models.Message]:
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
            .order_by(models.Message.timestamp.desc())
            .limit(num_messages)
        )
        msg_itr = await self.db.scalars(q)

        if num_tokens >= INF:
            return msg_itr.all()

        messages: list[models.Message] = []
        for msg in msg_itr:
            # TODO (Jonny): find a way to make sure this is in sync with the templates
            # this should hopefully be an upper bound on how bad it can be. (if we omit timestamps)
            formatted_content = f"[{msg.time_str}] {msg.content}"
            num_tokens -= self.tokenizer.length(formatted_content)
            if num_tokens < 0:
                break
            messages.append(msg)
        return messages

    async def get_memories(
        self, num_messages: int | None = None, num_tokens: int | None = None
    ) -> list[models.Memory]:
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
            return mem_itr.all()

        memories: list[models.Memory] = []
        for mem in mem_itr:
            num_tokens -= self.tokenizer.length(mem.content)
            if num_tokens < 0:
                break
            memories.append(mem)
        return memories

    async def get_monologues(
        self, num_messages: int | None = None, num_tokens: int | None = None
    ) -> list[models.Message]:
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
        msg_itr = await self.db.scalars(q)

        if num_tokens >= INF:
            return msg_itr.all()

        messages: list[models.Message] = []
        for msg in msg_itr:
            num_tokens -= self.tokenizer.length(msg.content)
            if num_tokens < 0:
                break
            messages.append(msg)
        return messages

    async def get_entity_context_summary(
        self, entity_name: str, n: int = 1
    ) -> list[models.EntityContextSummary]:
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
        summaries = await sa.scalars(q)
        return summaries.all()

    async def get_agent_summary(self, n: int = 1) -> list[models.AgentSummary]:
        if self.conversation_id is None:
            raise ValueError("Retrieving agent summary requires conversation_id.")
        q = (
            sa.select(models.AgentSummary)
            .where(models.AgentSummary.conversation_id == self.conversation_id)
            .order_by(models.AgentSummary.created_at.desc())
            .limit(n)
        )
        summaries = await sa.scalars(q)
        return summaries.all()

    async def increment_reflection_counter(self, importance: int) -> int:
        if self.conversation_id is None:
            raise ValueError(
                "Cannot increment counter without setting conversation id."
            )
        return await self.cache.reflection_counter(
            conversation_id=self.conversation_id
        ).increment(importance=importance)

    async def increment_entity_context_counter(self, importance: int) -> int:
        if self.conversation_id is None:
            raise ValueError(
                "Cannot increment counter without setting conversation id."
            )
        return await self.cache.entity_context_counter(
            conversation_id=self.conversation_id
        ).increment(importance=importance)

    async def increment_agent_summary_counter(self, importance: int) -> int:
        if self.conversation_id is None:
            raise ValueError(
                "Cannot increment counter without setting conversation id."
            )
        return await self.cache.agent_summary_counter(
            conversation_id=self.conversation_id
        ).increment(importance=importance)

    async def get_reflection_count(self) -> int:
        return await self.cache.reflection_counter(
            conversation_id=self.conversation_id
        ).get()

    async def get_entity_context_count(self) -> int:
        return await self.cache.entity_context_counter(
            conversation_id=self.conversation_id
        ).get()

    async def get_agent_summary_count(self) -> int:
        return await self.cache.agent_summary_counter(
            conversation_id=self.conversation_id
        ).get()

    async def set_reflection_count(self, value: int) -> None:
        return await self.cache.reflection_counter(
            conversation_id=self.conversation_id
        ).set(value=value)

    async def set_entity_context_count(self, value: int) -> None:
        return await self.cache.entity_context_counter(
            conversation_id=self.conversation_id
        ).set(value=value)

    async def set_agent_summary_count(self, value: int) -> None:
        return await self.cache.agent_summary_counter(
            conversation_id=self.conversation_id
        ).set(value=value)

    async def delete_document(self, doc: models.Document) -> None:
        await self.db.delete(doc)
        await self.db.commit()
        return None

    async def delete_monologue(self, monologue: models.Monologue) -> None:
        await self.db.delete(monologue)
        await self.db.commit()
        return None

    async def get_message_ancestors(
        self, message_id: uuid.UUID
    ) -> list[models.Message]:
        getter = (
            sa.select(models.Message)
            .where(models.Message.id == message_id)
            .cte(name="parent_for", recursive=True)
        )
        recursive_part = sa.select(models.Message).where(
            models.Message.id == getter.c.parent_id
        )
        with_recursive = getter.union_all(recursive_part)
        join_condition = models.Message.id == with_recursive.c.id
        final_query = sa.select(models.Message).select_from(
            with_recursive.join(models.Message, join_condition)
        )
        r = await self.db.scalars(final_query)
        return r.all()

    # (Jonny): is a flat list the best data structure to return here?
    # maybe like a hierarchical dict would be better?
    async def get_message_descendants(
        self, message_id: uuid.UUID
    ) -> list[models.Message]:
        getter = (
            sa.select(models.Message)
            .where(models.Message.id == message_id)
            .cte(name="children_for", recursive=True)
        )
        recursive_part = sa.select(models.Message).where(
            models.Message.parent_id == getter.c.id
        )
        with_recursive = getter.union_all(recursive_part)
        join_condition = models.Message.id == with_recursive.c.id
        final_query = sa.select(models.Message).select_from(
            with_recursive.join(models.Message, join_condition)
        )
        r = await self.db.scalars(final_query)
        return r.all()
