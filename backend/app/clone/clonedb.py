from abc import ABC, abstractmethod
import numpy as np
import uuid
from typing import Union
import sqlalchemy as sa
from clonr.data_structures import Document, Node, Dialogue, Memory, Message, Monologue
from . import retrieval
from app.embedding import EmbeddingClient
from app import models
from sqlalchemy.ext.asyncio import AsyncSession
from clonr.utils import get_current_datetime
from datetime import datetime
from clonr.tokenizer import Tokenizer
from app.db.cache import RedisCache


INF = 1_000_000


class CloneDB:
    def __init__(
        self,
        db: AsyncSession,
        cache: RedisCache,
        tokenizer: Tokenizer,
        embedding_client: EmbeddingClient,
        clone_id: str | uuid.UUID,
        conversation_id: str | uuid.UUID
    ):
        self.embedding_client = embedding_client
        self.db = db
        self.cache = cache
        self.tokenizer = tokenizer
        self.clone_id = clone_id
        self.conversation_id = conversation_id

    async def add_document(self, doc: Document, nodes: list[Node]):
        # don't re-do work if it's already there?
        if await self.get_document_by_hash(hash=doc.hash):
            return
        
        # Add embedding stuff. Doc embeddings are just the mean of all node embeddings
        embs = self.embedding_client.encode_passage([x.content for x in nodes])
        encoder_name = self.embedding_client.get_encoder_name()
        for i, node in enumerate(nodes):
            node.embedding = embs[i]
            node.embedding_model = encoder_name
        doc.embedding = np.array([node.embedding for node in nodes]).mean(0).tolist()
        if self.encoder.normalized:
            doc.embedding /= np.linalg.norm(doc.embedding)
        doc.embedding_model = self.encoder.name

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
            embedding_model=doc.embedding_model
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
                clone_id=self.clone_id
            )
            for node in nodes
        }

        # this will work for trees where each node has at most one parent!
        for node in nodes:
            node_models[node.id].parent = node_models.get(node.parent_id)

        self.db.add(doc_model)
        self.db.add_all(node_models.values())
        await self.db.commit()

    async def add_dialogues(self, dialogues: list[Dialogue]):
        """Requires that the dialogues have messages inside of them!"""
        embedding_model = self.embedding_client.encoder_name()
        for dialogue in dialogues:
            # batch encode
            embs = self.embedding_client.encode_passage([x.content for x in dialogue.messages])

            # update the messages in place
            for m, emb in zip(dialogue.messages, embs):
                m.embedding = emb
                m.embedding_model = embedding_model

            # we compute the dialogue embedding by averaging each of its messages
            # maybe good, maybe bad, fuck if I know.
            dialogue.embedding = np.array(embs).mean(0).tolist()
            if self.embedding_client.is_normalized():
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
                        clone_id=self.clone_id
                    )
                msgs.append(x)
            dlg = models.ExampleDialogue(
                source=dialogue.source,
                messages=msgs,
                embedding=dialogue.embedding,
                embedding_model=dialogue.embedding_model,
                clone_id=self.clone_id
            )

            self.db.add_all(msgs)
            self.db.add(dlg)
            await self.db.commit()

    async def add_monologues(self, monologues: list[Monologue]):
        monologue_models: list[models.Monologue] = []
        embeddings = self.embedding_client.encode_passage(
            [m.content for m in monologues]
        )
        embedding_model = self.embedding_client.encoder_name()
        for m, emb in zip(monologues, embeddings):
            m1 = models.Monologue(
                id=m.id,
                content=m.content,
                embedding=emb,
                embedding_model=embedding_model,
                hash=m.hash,
            )
            monologue_models.append(m1)
        self.db.add_all(monologue_models)
        await self.db.commit()

    async def add_memories(self, memories: list[Memory]):
        # batch embed
        embs = self.embedding_client.encode_passage([x.content for x in memories])
        embedding_model = self.embedding_client.encoder_name()

        # in-place update
        for m, emb in zip(memories, embs):
            m.embedding = emb
            m.embedding_model = embedding_model

        # add all of the memories
        for memory in memories:
            # This is unique to us, memories can be hierarchical (i.e. reflections)
            # and so we must pull all children that they depend on
            r = await self.db.scalars(sa.select(models.Memory).where(models.Memory.id.in_(tuple(memory.child_ids))))
            children = r.all()
            mem = models.Memory(
                content=memory.content,
                embedding=memory.embedding,
                embedding_model=memory.embedding_model,
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
    
    async def add_message(self, message: Message):
        if self.conversation_id is None:
            raise ValueError("Adding messages requires conversation_id.")
        msg = models.Message(
            id=message.id,
            content=message.content,
            sender_name=message.sender_name,
            timestamp=message.timestamp,
            is_clone=message.is_clone,
            clone_id=self.clone_id,
            conversation_id=self.conversation_id
        )
        self.db.add(msg)
        await self.db.commit()
        
    async def add_entity_context_summary(self, content: str, entity_name: str, timestamp: datetime = get_current_datetime()):
        if self.conversation_id is None:
            raise ValueError("Adding entity context summaries requires conversation_id.")
        obj = models.EntityContextSummary(
            content=content,
            entity_name=entity_name,
            timestamp=timestamp,
            clone_id=self.clone_id,
            conversation_id=self.conversation_id,
        )
        self.db.add(obj)
        await self.db.commit()
 
    async def add_agent_summary(self, content: str, timestamp: datetime = get_current_datetime()):
        if self.conversation_id is None:
            raise ValueError("Adding entity context summaries requires conversation_id.")
        obj = models.AgentSummary(
            content=content,
            timestamp=timestamp,
            clone_id=self.clone_id,
            conversation_id=self.conversation_id,
        )
        self.db.add(obj)
        await self.db.commit()

    async def query_nodes(self, query: str, params: retrieval.VectorSearchParams) -> list[retrieval.VectorSearchResult[models.Node]]:
        return await retrieval.vector_search(
            query=query,
            model=models.Node,
            params=params,
            db=self.db,
            embedding_client=self.embedding_client,
            tokenizer=self.tokenizer,
            filters=[models.Node.clone_id == self.clone_id]
        )    
        
    async def query_nodes_with_rerank(self, query: str, params: retrieval.ReRankSearchParams) -> list[retrieval.ReRankResult[models.Node]]:
        return await retrieval.rerank_search(
            query=query,
            model=models.Node,
            params=params,
            db=self.db,
            embedding_client=self.embedding_client,
            tokenizer=self.tokenizer,
            filters=[models.Node.clone_id == self.clone_id]
        )
    
    async def query_monologues(self, query: str, params: retrieval.VectorSearchParams) -> list[retrieval.VectorSearchResult[models.Monologue]]:
        return await retrieval.vector_search(
            query=query,
            model=models.Monologue,
            params=params,
            db=self.db,
            embedding_client=self.embedding_client,
            tokenizer=self.tokenizer,
            filters=[models.Monologue.clone_id == self.clone_id]
        )    
        
    async def query_monologues_with_rerank(self, query: str, params: retrieval.ReRankSearchParams) -> list[retrieval.ReRankResult[models.Monologue]]:
        return await retrieval.rerank_search(
            query=query,
            model=models.Monologue,
            params=params,
            db=self.db,
            embedding_client=self.embedding_client,
            tokenizer=self.tokenizer,
            filters=[models.Monologue.clone_id == self.clone_id]
        )       

    async def query_memories(self, query: str, params: retrieval.GenAgentsSearchParams, update_access_date: bool) -> list[retrieval.GenAgentsSearchResult[models.Memory]]:
        if self.conversation_id is None:
            raise ValueError("Retrieving memories requires conversation_id.")
        
        # We filter to retrieve either private memories for the conversation, or public memories
        # shared across all conversations
        is_public = sa.and_(models.Memory.clone_id == self.clone_id, models.Memory.is_shared == True)
        is_private = models.Memory.conversation_id == self.conversation_id
        filters = [sa.or_(is_public, is_private)]

        memory_results = await retrieval.gen_agents_search(
            query=query,
            model=models.Memory,
            params=params,
            db=self.db,
            embedding_client=self.embedding_client,
            tokenizer=self.tokenizer,
            filters=filters
        ) 

        # For memories, we have to update their `last_accessed_at` field each
        # time they are retrieved from the database
        if update_access_date:
            timestamp = get_current_datetime()
            for r in memory_results:
                r.model.last_accessed_at = timestamp
                self.db.add(r.model)
            self.db.commit()
        
    # get operations
    # should we use caching? this would grow without bound and be expensive af
    async def get_messages(self, num_messages: int | None = None, num_tokens: int | None = None) -> list[models.Message]:
        if self.conversation_id is None:
            raise ValueError("Retrieving memories requires conversation_id.")
        if num_messages is None or num_messages < 1:
            num_messages = INF
        q = (sa.select(models.Message)
            .where(models.Message.conversation_id == self.conversation_id)
            .order_by(models.Message.timestamp.desc())
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

    async def get_memories(self, num_messages: int | None = None, num_tokens: int | None = None) -> list[models.Memory]:
        # There is no last_accessed_at update for just getting memories, that only changes
        # when queried as part of a reflection or conversation
        if self.conversation_id is None:
            raise ValueError("Retrieving memories requires conversation_id.")
        if num_messages is None or num_messages < 1:
            num_messages = INF
        q = (sa.select(models.Memory)
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
    
    async def get_entity_context_summary(self, entity_name: str, n: int = 1) -> list[models.EntityContextSummary]:
        if self.conversation_id is None:
            raise ValueError("Retrieving entity context summary requires conversation_id.")
        q = sa.select(models.EntityContextSummary).where(models.EntityContextSummary.conversation_id == self.conversation_id).where(models.EntityContextSummary.entity_name == entity_name).order_by(models.EntityContextSummary.created_at.desc()).limit(n)
        summaries = await sa.scalars(q)
        return summaries.all()

    async def get_agent_summary(self, n: int = 1) -> list[models.AgentSummary]:
        if self.conversation_id is None:
            raise ValueError("Retrieving agent summary requires conversation_id.")
        q = sa.select(models.AgentSummary).where(models.AgentSummary.conversation_id == self.conversation_id).order_by(models.AgentSummary.created_at.desc()).limit(n)
        summaries = await sa.scalars(q)
        return summaries.all()

    async def increment_reflection_counter(self, importance: int) -> int:
        return await self.cache.reflection_counter(clone_id=self.clone_id).increment(importance=importance)

    async def increment_entity_context_counter(self, importance: int) -> int:
        return await self.cache.entity_context_counter(clone_id=self.clone_id).increment(importance=importance)

    async def increment_agent_summary_counter(self, importance: int) -> int:
        return await self.cache.agent_summary_counter(clone_id=self.clone_id).increment(importance=importance)

    async def get_reflection_count(self) -> int:
        return await self.cache.reflection_counter(clone_id=self.clone_id).get()
    
    async def get_entity_context_count(self) -> int:
        return await self.cache.entity_context_counter(clone_id=self.clone_id).get()

    async def get_agent_summary_count(self) -> int:
        return await self.cache.agent_summary_counter(clone_id=self.clone_id).get()
    
    async def set_reflection_count(self, value: int) -> None:
        return await self.cache.reflection_counter(clone_id=self.clone_id).set(value=value)
    
    async def set_entity_context_count(self, value: int) -> None:
        return await self.cache.entity_context_counter(clone_id=self.clone_id).set(value=value)

    async def set_agent_summary_count(self, value: int) -> None:
        return await self.cache.agent_summary_counter(clone_id=self.clone_id).set(value=value)