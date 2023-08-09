import sqlalchemy as sa
from fastapi import BackgroundTasks
from redis.asyncio import Redis
from sqlalchemy.ext.asyncio import AsyncSession

from app import models, schemas
from app.clone.types import (
    AdaptationStrategy,
    GenAgentsSearchParams,
    InformationStrategy,
    MemoryStrategy,
    ReRankSearchParams,
    VectorSearchParams,
)
from app.embedding import EmbeddingClient
from clonr import generate, templates
from clonr.data_structures import Memory, Message, Monologue
from clonr.llms import LLM
from clonr.tokenizer import Tokenizer

# TODO (Jonny): protect the route?
# from app.external.moderation import openai_moderation_check
from .cache import CloneCache
from .db import CloneDB

# the Gen Agents paper uses a threshold of 150 (that's what he said during the talk)
# min memory importance is 1 and max is 10, so a score of 100 ~ 20 memories on avg.
# reflections peak at the last 100 memories so this is actually quite short
# stagger the values so that they don't trigger on the same received_message
SEED_IMPORTANCE: int = 4
REFLECTION_THRESHOLD: int = 100
AGENT_SUMMARY_THRESHOLD: int = 120
ENTITY_CONTEXT_THRESHOLD: int = 140

NUM_RECENT_MSGS_FOR_QUERY = 4


def get_num_monologue_tokens(extra_space: bool) -> int:
    return 350 if extra_space else 250


def get_num_fact_tokens(extra_space: bool) -> int:
    return 150 if extra_space else 100


def get_num_memory_tokens(extra_space: bool) -> int:
    return 200 if extra_space else 100


class ControllerException(Exception):
    pass


class UnsupportedStrategy(Exception):
    pass


class Controller:
    def __init__(
        self,
        llm: LLM,
        clonedb: CloneDB,
        clone: models.Clone,
        conversation: models.Conversation,
        background_tasks: BackgroundTasks,
    ):
        self.llm = llm
        self.clonedb = clonedb
        self.clone = clone
        self.conversation = conversation
        self.background_tasks = background_tasks

    @property
    def memory_strategy(self) -> schemas.MemoryStrategy:
        return self.conversation.memory_strategy

    @property
    def information_strategy(self) -> schemas.InformationStrategy:
        return self.conversation.information_strategy

    @property
    def adaptation_strategy(self) -> schemas.AdaptationStrategy:
        return self.conversation.adaptation_strategy

    @property
    def user_name(self) -> str:
        return self.conversation.user_name

    @property
    def agent_summary_threshold(self) -> int:
        return self.conversation.agent_summary_threshold

    @property
    def reflection_threshold(self) -> int:
        return self.conversation.reflection_threshold

    @property
    def entity_context_threshold(self) -> int:
        return self.conversation.entity_context_threshold

    @classmethod
    async def create_conversation(
        cls,
        obj: schemas.ConversationCreate,
        clone: models.Clone,
        db: AsyncSession,
        user: models.User,
        conn: Redis,
        tokenizer: Tokenizer,
        embedding_client: EmbeddingClient,
    ) -> models.Conversation:
        data = obj.model_dump(exclude_none=True)
        convo = models.Conversation(**data, user_id=user.id)
        if obj.adaptation_strategy != AdaptationStrategy.static:
            convo.agent_summary_threshold = AGENT_SUMMARY_THRESHOLD
            convo.entity_context_threshold = ENTITY_CONTEXT_THRESHOLD
            convo.reflection_threshold = REFLECTION_THRESHOLD
        db.add(convo)
        await db.commit()
        await db.refresh(convo)

        cache = CloneCache(conn=conn)
        clonedb = CloneDB(
            db=db,
            cache=cache,
            tokenizer=tokenizer,
            embedding_client=embedding_client,
            clone_id=obj.clone_id,
            conversation_id=convo.id,
        )

        if convo.memory_strategy == MemoryStrategy.long_term:
            # counters for different strategies
            await clonedb.set_reflection_count(0)

            if convo.adaptation_strategy != AdaptationStrategy.static:
                await clonedb.set_agent_summary_count(0)
                await clonedb.set_entity_context_count(0)

            # add seed memories
            content = f"I started a conversation with {convo.user_name}"
            seed_memories = [Memory(content=content, importance=SEED_IMPORTANCE)]
            await clonedb.add_memories(seed_memories)

        # add greeting message
        greeting_message = Message(
            content=clone.greeting_message,
            is_clone=True,
            sender_name=clone.name,
            parent_id=None,
        )
        await clonedb.add_message(greeting_message)

        return convo

    async def _add_private_memory(self, content: str) -> models.Memory:
        if self.memory_strategy != MemoryStrategy.long_term:
            raise ControllerException(
                f"Cannot add memories with memory strategy {self.memory_strategy}"
            )

        importance = await generate.rate_memory(llm=self.llm, memory=content)

        reflection_count = await self.clonedb.increment_reflection_counter(
            importance=importance
        )

        memory_struct = Memory(content=content, importance=importance, is_shared=False)
        memory = await self.clonedb.add_memories([memory_struct])

        if reflection_count >= self.reflection_threshold:
            self.background_tasks.add_task(self._reflect)
            await self.clonedb.set_reflection_count(0)

        if self.adaptation_strategy != AdaptationStrategy.static:
            agent_summary_count = await self.clonedb.increment_agent_summary_counter(
                importance=importance
            )

            if agent_summary_count >= self.agent_summary_threshold:
                self.background_tasks.add_task(self._agent_summary_compute)
                await self.clonedb.set_agent_summary_count(0)

            entity_context_count = await self.clonedb.increment_entity_context_counter(
                importance=importance
            )

            if entity_context_count >= self.entity_context_threshold:
                self.background_tasks.add_task(self._entity_context_compute)
                await self.clonedb.set_entity_context_count(0)

        return memory[0]

    async def add_user_message(
        self, msg_create: schemas.MessageCreate
    ) -> models.Message:
        data = msg_create.model_dump(exclude_unset=True)
        msg_struct = Message(sender_name=self.user_name, is_clone=True, **data)
        msg = await self.clonedb.add_message(msg_struct)

        if self.memory_strategy == MemoryStrategy.long_term:
            mem_content = f'{msg.sender_name} messaged me, "{msg.content}"'
            self._add_private_memory(content=mem_content)

        return msg

    # TODO (Jonny): ensure auth happens further up the chain at the route level
    @classmethod
    async def add_public_memory(
        cls,
        mem_create: schemas.SharedMemoryCreate,
        clone: models.Clone,
        llm: LLM,
        db: AsyncSession,
        conn: Redis,
        tokenizer: Tokenizer,
        embedding_client: EmbeddingClient,
    ) -> models.Memory:
        # NOTE (Jonny): we have to do a mass update across potentially many redis
        # keys, so we use a pipeline to batch all requests on the client side.
        # we get a huge boost in efficiency at the cost of increment things we might
        # not need to track (like agent_summaries and entity_context). Note we do not
        # trigger reflections, as we don't want to surge LLM calls for popular clones
        cache = CloneCache(conn=conn)
        clonedb = CloneDB(
            db=db,
            cache=cache,
            tokenizer=tokenizer,
            embedding_client=embedding_client,
            clone_id=clone.clone_id,
            conversation_id=None,
        )
        # add to the database
        if mem_create.importance is None:
            mem_create.importance = await generate.rate_memory(
                llm=llm, memory=mem_create.content
            )
        data = mem_create.model_dump(exclude_unset=True)
        memory_struct = Memory(is_shared=True, **data)
        memory = await clonedb.add_memories([memory_struct])

        # update all of the counters
        r = await db.scalars(
            sa.select(models.Conversation.id).where(
                models.Conversation.clone_id == clone.id
            )
        )
        conversation_ids = r.all()
        await cache.increment_all_counters(
            conversation_ids=conversation_ids, importance=memory.importance
        )
        return memory

    async def _reflect(self, num_memories: int, num_tokens: int) -> list[models.Memory]:
        # TODO (Jonny): add token guard to make sure prompt is under limit
        # typical value is 100 memories
        memories = await self.clonedb.get_memories(
            num_messages=num_memories, num_tokens=num_tokens
        )

        queries = await generate.reflection_queries_create(
            llm=self.llm, memories=memories
        )

        retrieved_memories: list[models.Memory] = []
        # 15 * 5 = 75 memories pulled.
        params = GenAgentsSearchParams(max_items=max(1, num_memories // 5))

        for q in queries:
            cur = await self.clonedb.query_memories(query=q, params=params)
            retrieved_memories.extend(cur)
        retrieved_memories.sort(key=lambda x: x.timestamp)

        # TODO (Jonny): add token guard
        reflections = await generate.reflections_create(
            llm=self.llm, memories=retrieved_memories
        )

        mems = await self.clonedb.add_memories(reflections)
        await self.clonedb.set_reflection_count(0)

        return mems

    async def _agent_summary_compute(self) -> models.AgentSummary:
        # NOTE (Jonny): the queries are from clonr/templates/agent_summary
        # the default questions. In this step.
        # We use I/my since it's better for similarity search here.
        queries = [
            "How would one describe my core characteristics?",
            "How would one describe my feelings about my recent progress in life?",
        ]
        retrieved_memories: list[models.Memory] = []
        params = GenAgentsSearchParams(max_items=25)
        for q in queries:
            cur = await self.clonedb.query_memories(query=q, params=params)
            retrieved_memories.extend(cur)
        retrieved_memories.sort(key=lambda x: x.timestamp)

        char = self.clone.name
        short_description = self.clone.short_description

        match self.adaptation_strategy:
            case AdaptationStrategy.dynamic:
                long_description = self.clone.long_description
                # NOTE (Jonny): we're shifting towards more dynamic here
                # not sure if this is a good idea or not!
                if prev_summaries := await self.clonedb.get_agent_summary(n=1):
                    long_description = prev_summaries[0]
            case AdaptationStrategy.fluid:
                long_description = None
            case _:
                # not sure if this is a good idea, might want to break earlier in this function.
                raise UnsupportedStrategy(
                    f"Adaptation strategy ({self.adaptation_strategy}) is not compatible with agent summaries."
                )

        content = await generate.agent_summary(
            llm=self.llm,
            char=char,
            memories=retrieved_memories,
            short_description=short_description,
            long_description=long_description,
        )
        agent_summary = await self.clonedb.add_agent_summary(content=content)

        return agent_summary

    async def _entity_context_compute(self):
        if self.adaptation_strategy == AdaptationStrategy.static:
            raise UnsupportedStrategy(
                f"Adaptation strategy ({self.adaptation_strategy}) is not compatible with agent summaries."
            )
        # We adapt the in-template questions from clonr/templates/entity_relationship
        queries = [
            f"What is my relationship to {self.user_name}?",
            f"What do I think of, and how do I feel about {self.user_name}?",
        ]
        statements: list[models.Memory] = []
        params = GenAgentsSearchParams(max_items=30)
        for q in queries:
            cur = await self.clonedb.query_memories(query=q, params=params)
            statements.extend(cur)
        statements.sort(key=lambda x: x.timestamp)

        char = self.clone.name
        entity = self.user_name

        content = await generate.entity_context_create(
            llm=self.llm,
            char=char,
            entity=entity,
            statements=statements,
        )
        entity_summary = await self.clonedb.add_entity_context_summary(
            content=content, entity_name=entity
        )

        return entity_summary

    async def set_revision_as_main(
        self, rev_update: schemas.RevisionUpdate
    ) -> models.Message:
        """Given a list of current revisions, this sets the given one as part of the main
        message thread. This should trigger whenever users click the revision arrows."""
        parent = await self.clonedb.db.get(models.Message, rev_update.message_id)
        msg = None
        if len(parent.children) < 2:
            raise ControllerException(
                f"Message {rev_update.message_id} is not part of a revision group."
            )
        for c in parent.children:
            c.is_main = rev_update.message_id == c.id
            if c.children:
                raise ControllerException(
                    "Revisions can only be set for the most recent regeneration."
                )
            if rev_update.message_id == c.id:
                msg = c
                self.clonedb.db.add(msg)
            else:
                self.clonedb.db.add(c)
        if msg is None:
            raise ControllerException(
                "Internal error. Connection between revision and messages not found."
            )
        await self.clonedb.db.commit()
        return msg

    async def _generate_msg_queries(
        self, num_messges: int | None, num_tokens: int | None
    ) -> list[str]:
        recent_msgs = await self.clonedb.get_messages(
            num_messages=num_messges, num_tokens=num_tokens
        )
        recent_msgs = list(reversed(recent_msgs))
        entity_name = self.user_name
        agent_summary = None
        entity_context_summary = None

        if self.memory_strategy == MemoryStrategy.long_term:
            agent_summary = await self.clonedb.get_agent_summary(n=1)
            entity_context_summary = await self.clonedb.get_entity_context_summary(
                entity_name=entity_name, n=1
            )
            if not agent_summary:
                agent_summary = None
            if not entity_context_summary:
                entity_context_summary = None

        queries = await generate.message_queries_create(
            llm=self.llm,
            char=self.clone.name,
            short_description=self.clone.short_description,
            agent_summary=agent_summary,
            entity_context_summary=entity_context_summary,
            entity_name=entity_name,
            messages=recent_msgs,
        )

        return queries

    async def _generate_zero_memory_message(self) -> models.Message:
        if self.information_strategy == InformationStrategy.internal:
            queries = await self._generate_msg_queries(
                num_messges=NUM_RECENT_MSGS_FOR_QUERY
            )
            # NOTE (Jonny): we don't want duplicate monologues, so make one query.
            mashed_query = " ".join(queries)
            results = await self.clonedb.query_monologues(
                query=mashed_query,
                params=VectorSearchParams(max_items=25, max_tokens=512),
            )
            monologues = [
                Monologue(
                    id=m.model.id,
                    content=m.model.content,
                    source=m.model.source,
                    hash=m.model.hash,
                )
                for m in results
            ]

            # NOTE (Jonny): the odds of duplicates are low for info-extraction, so
            # do the higher accuracy info retrieval step. Weird we take str and not nodes.
            # whatever, not gonna redo it.
            facts: list[str] = []
            for q in queries:
                cur = await self.clonedb.query_nodes_with_rerank(
                    query=q, params=ReRankSearchParams(max_items=3, max_tokens=170)
                )
                for c in cur:
                    facts.append(c.model.content)
        else:
            # TODO (Jonny): trying to avoid a ~500 token request by eliminating the
            # monologue query. We are always running for the thrill of it.
            monologues = [
                Monologue(
                    id=m.model.id,
                    content=m.model.content,
                    source=m.model.source,
                    hash=m.model.hash,
                )
                for m in (await self.clonedb.get_monologues(num_tokens=512))
            ]
            facts = None

        tokens_remaining = self.llm.context_length

        cur_prompt = templates.ZeroMemoryMessage.render(
            char=self.clone.name,
            user_name=self.user_name,
            short_description=self.clone.short_description,
            long_description=self.clone.long_description,
            monologues=monologues,
            facts=facts,
            llm=self.llm,
            messages=[],
        )
        tokens_remaining -= self.llm.num_tokens(cur_prompt)
        tokens_remaining -= generate.Params.generate_zero_memory_message.max_tokens

        recent_msgs = await self.clonedb.get_messages(num_tokens=tokens_remaining)
        parent_id = recent_msgs[0].id if recent_msgs else None
        messages = list(reversed(recent_msgs))

        new_msg_content = await generate.generate_zero_memory_message(
            char=self.clone.name,
            user_name=self.user_name,
            short_description=self.clone.short_description,
            long_description=self.clone.long_description,
            monologues=monologues,
            messages=messages,
            facts=facts,
            llm=self.llm,
            use_timestamps=False,
        )
        new_msg_struct = Message(
            content=new_msg_content,
            sender_name=self.clone.name,
            is_clone=True,
            parent_id=parent_id,
        )
        new_msg = await self.clonedb.add_message(new_msg_struct)

        return new_msg

    async def _generate_long_term_memory_message(self):
        # short and long descriptions (max ~540 tokens)
        # (check generate.Params for more details)
        char = self.clone.name
        short_description = self.clone.short_description
        long_description = self.clone.long_description

        # generate the queries used for retrieval ops
        queries = await self._generate_msg_queries(
            num_messges=NUM_RECENT_MSGS_FOR_QUERY
        )
        mashed_query = " ".join(queries)

        # If we aren't using agent summaries and entity summaries,
        # that frees up ~1024 tokens, which we can use elsewhere. Figure
        # out if we have that space first!
        agent_summary: str | None = None
        entity_context_summary: str | None = None
        if self.memory_strategy == MemoryStrategy.long_term:
            match self.adaptation_strategy:
                case AdaptationStrategy.static:
                    pass
                case AdaptationStrategy.dynamic | AdaptationStrategy.fluid:
                    e_summ = await self.clonedb.get_entity_context_summary(
                        entity_name=self.user_name, n=1
                    )
                    entity_context_summary = e_summ[0] if e_summ else None

                    a_summ = await self.clonedb.get_agent_summary(n=1)

                    if self.adaptation_strategy == AdaptationStrategy.dynamic:
                        agent_summary = a_summ[0] if a_summ else None
                    elif self.adaptation_strategy == AdaptationStrategy.fluid:
                        # NOTE (Jonny): this is the key difference for fluid bots. We continually
                        # replace the long description, so the bot can change quickly!
                        long_description = a_summ[0] if a_summ else None
                case _:
                    raise UnsupportedStrategy(
                        f"Invalid adaptation strategy: {self.adaptation_strategy}"
                    )

        # fact and memory get 3x multiplier. Memory gets another penalty for having to
        # include like 16 tokens for timestamps each memory (around 150 extra in total)
        extra_space = agent_summary is None and entity_context_summary is None
        monologue_tokens = get_num_monologue_tokens(extra_space)
        fact_tokens = get_num_fact_tokens(extra_space)
        memory_tokens = get_num_memory_tokens(extra_space)

        # Retrieve relevant monologues (max 300 tokens)
        results = await self.clonedb.query_monologues_with_rerank(
            query=mashed_query,
            params=ReRankSearchParams(max_items=10, max_tokens=monologue_tokens),
        )
        monologues = [
            Monologue(
                id=m.model.id,
                content=m.model.content,
                source=m.model.source,
                hash=m.model.hash,
            )
            for m in results
        ]

        # Retrieve relevant facts (max 450 tokens)
        facts: list[str] | None = None
        if self.information_strategy in [
            InformationStrategy.internal,
            InformationStrategy.external,
        ]:
            facts = []
            for q in queries:
                cur = await self.clonedb.query_nodes_with_rerank(
                    query=q,
                    params=ReRankSearchParams(max_items=3, max_tokens=fact_tokens),
                )
                facts.extend([c.model.content for c in cur])

        # Retrieve relevant memories (max 512 tokens)
        memories: list[Memory] = []
        vis_mem: set[str] = set()
        for q in queries:
            cur = await self.clonedb.query_memories(
                q,
                params=GenAgentsSearchParams(max_tokens=memory_tokens, max_items=3),
                update_access_date=False,
            )
            for c in cur:
                if str(c.model.id) not in vis_mem:
                    mem = Memory(
                        id=c.model.id,
                        content=c.model.content,
                        timestamp=c.model.timestamp,
                        importance=c.model.importance,
                        is_shared=c.model.is_shared,
                    )
                    memories.append(mem)
                vis_mem.add(str(c.model.id))

        tokens_remaining = self.llm.context_length

        cur_prompt = templates.LongTermMemoryMessage.render(
            char=char,
            user_name=self.user_name,
            short_description=short_description,
            long_description=long_description,
            monologues=monologues,
            facts=facts,
            memories=memories,
            agent_summary=agent_summary,
            entity_context_summary=entity_context_summary,
            llm=self.llm,
            messages=[],
        )
        # we will prune overlapping memories with messages later, so this is a conservative
        # overcount
        tokens_remaining -= self.llm.num_tokens(cur_prompt)
        tokens_remaining -= generate.Params.generate_long_term_memory_message.max_tokens

        # we should have 4096 - (560_long + 250_mono + 300_fact + 300_mem)
        # - 512_gen - 1024_dyn ~ 1100 remaining for past messages.
        print(tokens_remaining)

        recent_msgs = await self.clonedb.get_messages(num_tokens=tokens_remaining)
        parent_id = recent_msgs[0].id if recent_msgs else None
        messages = list(reversed(recent_msgs))
        oldest_msg_timestamp = messages[0].timestamp

        # NOTE (Jonny): Since only shared memories can be non-messages at the moment,
        # we can just remove any memory that is more recent than the oldest message
        # and that is not shared. Pretty simple fix to prevent overlap
        memories = [
            m for m in memories if m.is_shared or m.timestamp < oldest_msg_timestamp
        ]

        new_msg_content = await generate.generate_long_term_memory_message(
            char=self.clone.name,
            user_name=self.user_name,
            short_description=self.clone.short_description,
            long_description=self.clone.long_description,
            monologues=monologues,
            messages=messages,
            memories=memories,
            agent_summary=agent_summary,
            entity_context_summary=entity_context_summary,
            facts=facts,
            llm=self.llm,
            use_timestamps=True,
        )
        new_msg_struct = Message(
            content=new_msg_content,
            sender_name=self.clone.name,
            is_clone=True,
            parent_id=parent_id,
        )
        new_msg = await self.clonedb.add_message(new_msg_struct)

        return new_msg

    async def generate_message(self):
        """This method is the entire IP of this whole entire application, the goddamn GOAT.
        Calls all of the subroutines and returns the next message response for the clone.
        """
        # TODO (Jonny): Add a telemetry packet here with things like prompt size, n_msgs,
        # n_memories, n_pruned_memories, n_facts, fact_chars, mem_chars, etc.
        match self.memory_strategy:
            case MemoryStrategy.none:
                return await self._generate_zero_memory_message()
            case MemoryStrategy.short_term | MemoryStrategy.long_term:
                # the only diff is in adaptation strategy I guess, so it's
                # all just handled in the same function
                return self._generate_long_term_memory_message()
            case _:
                raise UnsupportedStrategy(
                    f"Invalid memory strategy: {self.memory_strategy}"
                )

    @classmethod
    async def generate_long_description(
        cls, llm: LLM, clone: models.Clone, clonedb: CloneDB
    ) -> models.LongDescription:
        # This can be an expensive computation as it will cost roughly
        # the number of tokens in all documents combined, plus some
        # factor like 2 * 512 * (tot_tokens / llm.context_length)
        r = await clonedb.db.scalars(
            sa.select(models.Document).order_by(models.Document.type)
        )
        docs = r.all()
        long_desc = await generate.long_description_create(
            llm=llm, short_description=clone.short_description, docs=docs
        )
        clone.long_description = long_desc
        long_desc_model = models.LongDescription(
            content=long_desc, documents=docs, clone=clone
        )
        clonedb.db.add(clone)
        clonedb.db.add(long_desc_model)
        await clonedb.db.commit()
        await clonedb.db.refresh(long_desc_model, ["documents"])
        return long_desc_model
