import re
import uuid

import sqlalchemy as sa
from fastapi import BackgroundTasks, HTTPException, status
from loguru import logger
from opentelemetry import trace
from redis.asyncio import Redis
from sqlalchemy.ext.asyncio import AsyncSession

from app import models, schemas
from app.embedding import EmbeddingClient
from clonr import generate, templates
from clonr.data_structures import Memory, Message, Monologue
from clonr.llms import LLM
from clonr.tokenizer import Tokenizer

# TODO (Jonny): protect the route?
# from app.external.moderation import openai_moderation_check
from .cache import CloneCache
from .db import CloneDB
from .types import (
    AdaptationStrategy,
    GenAgentsSearchParams,
    InformationStrategy,
    MemoryStrategy,
    ReRankSearchParams,
    VectorSearchParams,
)

tracer = trace.get_tracer(__name__)

# the Gen Agents paper uses a threshold of 150 (that's what he said during the talk)
# min memory importance is 1 and max is 10, so a score of 100 ~ 20 memories on avg.
# reflections peak at the last 100 memories so this is actually quite short
# stagger the values so that they don't trigger on the same received_message
SEED_IMPORTANCE: int = 4
REFLECTION_THRESHOLD: int = 100
AGENT_SUMMARY_THRESHOLD: int = 120
ENTITY_CONTEXT_THRESHOLD: int = 140

NUM_RECENT_MSGS_FOR_QUERY = 4
NUM_REFLECTION_MEMORIES = 60


def get_num_monologue_tokens(extra_space: bool) -> int:
    return 350 if extra_space else 250


def get_num_fact_tokens(extra_space: bool) -> int:
    return 150 if extra_space else 100


def get_num_memory_tokens(extra_space: bool) -> int:
    return 200 if extra_space else 100


# TODO (Jonny): we need a way to make sure that both this and the DateFormat are always in sync
# this covers the human readable, relative, and isoformat cases
def remove_timestamps_from_msg(content: str) -> str:
    # The first are days of the week and shit
    # the second is a date like 2023-01-01
    # the last covers stuff like 12 hours ago, 12 hours 5 mintues ago, 12 hours and 5 minutes ago
    pattern = r"^\[(Monday|Tuesday|Wednesday|Thursday|Friday|Saturday|Sunday|Yesterday|Today|\d\d\d\d\-\d\d\-\d\d|\d+\s\w+\sago|\d+\s\w+\sand|\d+\s\w+\s\d+).*?\]"  # noqa
    lines = re.split(pattern, content)
    # the pattern alternates content, split-token, content, split-token.
    return "\n".join(lines[::2])


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
            user_id=user.id,
        )

        # counters for different strategies. Set all just to be safe
        await clonedb.set_reflection_count(0)
        await clonedb.set_agent_summary_count(0)
        await clonedb.set_entity_context_count(0)

        if convo.memory_strategy != MemoryStrategy.none:
            # add seed memories
            # TODO (Jonny): Should we make this something like "I am eager to learn more about {{user}}?"
            # in order to drive the conversation, or make this configurable to creators?
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

        if convo.memory_strategy != MemoryStrategy.none:
            # NOTE (Jonny): to make things easier, we don't count the greeting message towards any of the
            # memory-based counters. We can assume things start at zero.
            mem_content = f'I messaged {convo.user_name}, "{greeting_message.content}"'
            memory_struct = Memory(content=mem_content, importance=3, is_shared=False)
            await clonedb.add_memories([memory_struct])

        return convo

    @tracer.start_as_current_span("add_private_memory")
    async def _add_private_memory(self, content: str) -> models.Memory:
        if self.memory_strategy == MemoryStrategy.none:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Cannot add memories with memory strategy {self.memory_strategy}",
            )

        importance = await generate.rate_memory(llm=self.llm, memory=content)

        reflection_count = await self.clonedb.increment_reflection_counter(
            importance=importance
        )

        memory_struct = Memory(content=content, importance=importance, is_shared=False)
        memory = await self.clonedb.add_memories([memory_struct])

        if reflection_count >= self.reflection_threshold:
            self.background_tasks.add_task(self._reflect, NUM_REFLECTION_MEMORIES)
            await self.clonedb.set_reflection_count(0)

        if (
            self.memory_strategy == MemoryStrategy.long_term
            and self.adaptation_strategy != AdaptationStrategy.static
        ):
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

    @tracer.start_as_current_span("add_user_message")
    async def add_user_message(
        self, msg_create: schemas.MessageCreate
    ) -> models.Message:
        data = msg_create.model_dump(exclude_unset=True)

        # NOTE (Jonny): we aren't letting users upload parent_id, that shit is too
        # risky, one bad user that sees our API could fuck up their own chat history
        # and we would also need to put an auth guard to prevent sending a parent_id
        # without the proper auth.
        parent_id = (await self.clonedb.get_messages(num_messages=1))[0].id

        # TODO (Jonny): msg + mem should really occur under the same db commit
        msg_struct = Message(
            sender_name=self.user_name, is_clone=False, parent_id=parent_id, **data
        )
        msg = await self.clonedb.add_message(msg_struct)

        if self.memory_strategy != MemoryStrategy.none:
            mem_content = f'{msg.sender_name} messaged me, "{msg.content}"'
            self.background_tasks.add_task(
                self._add_private_memory, content=mem_content
            )

        return msg

    # TODO (Jonny): ensure auth happens further up the chain at the route level
    @tracer.start_as_current_span("add_public_memory")
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
            user_id=None,
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

    @tracer.start_as_current_span("reflect")
    async def _reflect(self, num_memories: int) -> list[models.Memory]:
        # typical value is 100 memories. the query template is 112 tokens so we have lots of room here
        # assume a max output of 512 tokens for questions
        num_tokens = self.llm.context_length - 512 - 120
        logger.info(f"Reflection triggered for conversation {self.conversation.id}")
        memories = await self.clonedb.get_memories(
            num_messages=num_memories, num_tokens=num_tokens
        )

        # the default value is 3, and the defintion should probably be pushed up higher in the stack
        queries = await generate.reflection_queries_create(
            llm=self.llm,
            memories=memories,
        )

        retrieved_memories: list[models.Memory] = []
        # this ensures we pull roughly a little less than the number of memories pulled above
        # e.g. at 3 queries and 60 msgs, this would yield 45 msgs
        max_items = num_memories // (1 + len(queries))
        max_items = max(1, max_items)
        # the prompt here is 180 tokens, so just take off another 860 tokens
        num_tokens -= 60
        params = GenAgentsSearchParams(max_items=max_items, max_tokens=num_tokens)

        for q in queries:
            cur = await self.clonedb.query_memories(
                query=q, params=params, update_access_date=True
            )
            retrieved_memories.extend([c.model for c in cur])
        retrieved_memories.sort(key=lambda x: x.timestamp)

        reflections_without_ratings = await generate.reflections_create(
            llm=self.llm, memories=retrieved_memories
        )
        reflections: list[Memory] = []
        for r in reflections_without_ratings:
            data = r.model_dump()
            data["importance"] = await generate.rate_memory
            refl = Memory(**data)
            reflections.append(refl)

        mems = await self.clonedb.add_memories(reflections)
        await self.clonedb.set_reflection_count(0)

        return mems

    @tracer.start_as_current_span("agent_summary_compute")
    async def _agent_summary_compute(self) -> models.AgentSummary:
        # NOTE (Jonny): the queries are from clonr/templates/agent_summary
        # the default questions. In this step.
        # We use I/my since it's better for similarity search here.
        logger.info(
            f"Agent summary compute triggered for conversation {self.conversation.id}"
        )
        queries = [
            "How would one describe my core characteristics?",
            "How would one describe my feelings about my recent progress in life?",
        ]
        retrieved_memories: list[models.Memory] = []
        # The prompt here is about 180 tokens base + 512 long desc.
        max_tokens = self.llm.context_length - 190 - 512 - 512
        max_tokens = int(max_tokens // max(1, len(queries)))
        params = GenAgentsSearchParams(max_items=12, max_tokens=max_tokens)
        for q in queries:
            # TODO (Jonny): should we update access date for this?
            cur = await self.clonedb.query_memories(
                query=q, params=params, update_access_date=True
            )
            retrieved_memories.extend([c.model for c in cur])
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
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail=f"Adaptation strategy ({self.adaptation_strategy}) is not compatible with agent summaries.",
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

    @tracer.start_as_current_span("entity_context_compute")
    async def _entity_context_compute(self):
        logger.info(
            f"Entity context compute triggered for conversation {self.conversation.id}"
        )
        if self.adaptation_strategy == AdaptationStrategy.static:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Adaptation strategy ({self.adaptation_strategy}) is not compatible with agent summaries.",
            )
        # get the last entity summary
        tmp = await self.clonedb.get_entity_context_summary(
            n=1, entity_name=self.user_name
        )
        prev_entity_summary = tmp[0] if tmp else None

        # We adapt the in-template questions from clonr/templates/entity_relationship
        queries = [
            f"What is my relationship to {self.user_name}?",
            f"What do I think of, and how do I feel about {self.user_name}?",
        ]
        statements: list[models.Memory] = []
        # The prompt here is about 150 tokens base plus max 512 prev entity context + generation
        max_tokens = self.llm.context_length - 150 - 512 - 512
        max_tokens = int(max_tokens // max(1, len(queries)))
        params = GenAgentsSearchParams(max_items=12, max_tokens=max_tokens)
        for q in queries:
            # TODO (Jonny): should we update access date for this?
            cur = await self.clonedb.query_memories(
                query=q, params=params, update_access_date=True
            )
            statements.extend([c.model for c in cur])
        statements.sort(key=lambda x: x.timestamp)

        char = self.clone.name
        entity = self.user_name

        content = await generate.entity_context_create(
            llm=self.llm,
            char=char,
            entity=entity,
            statements=statements,
            prev_entity_summary=prev_entity_summary,
        )
        entity_summary = await self.clonedb.add_entity_context_summary(
            content=content, entity_name=entity
        )

        return entity_summary

    @tracer.start_as_current_span("set_revision_as_main")
    async def set_revision_as_main(self, message_id: uuid.UUID) -> models.Message:
        """Given a list of current revisions, this sets the given one as part of the main
        message thread. This should trigger whenever users click the revision arrows."""
        if not (last_messages := await self.clonedb.get_messages(num_messages=1)):
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="There are no current messages in the conversation.",
            )
        last_msg = last_messages[0]
        if not last_msg.is_clone:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Can only set a revision if the last message was from the Clone.",
            )
        if last_msg.parent_id is None:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Revisions on the greeting message are not allowed.",
            )
        revisions = (
            await self.clonedb.db.scalars(
                sa.select(models.Message).where(
                    models.Message.parent_id == last_msg.parent_id
                )
            )
        ).all()
        if len(revisions) < 2:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="There is only one current generation, and so there are no revisions to set as main.",
            )
        msg: models.Message | None = None
        for rev in revisions:
            if rev.id == message_id:
                rev.is_main = True
                msg = rev
            else:
                rev.is_main = False
        if msg is None:
            detail = (
                f"Message {message_id} is not an eligible revision to select. "
                f"Eligible revisions are: {revisions}",
            )
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=detail)
        await self.clonedb.db.commit()
        await self.clonedb.db.refresh(msg)
        return msg

    @tracer.start_as_current_span("generate_message_queries")
    async def _generate_msg_queries(
        self, num_messges: int | None, num_tokens: int | None
    ) -> list[str]:
        recent_msgs = await self.clonedb.get_messages(
            num_messages=num_messges, num_tokens=num_tokens
        )
        recent_msgs_reversed = list(reversed(recent_msgs))
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

        # This should always return a value, we catch any exceptions in the generate
        # function and default to returning the entire output as a query
        queries = await generate.message_queries_create(
            llm=self.llm,
            char=self.clone.name,
            short_description=self.clone.short_description,
            agent_summary=agent_summary,
            entity_context_summary=entity_context_summary,
            entity_name=entity_name,
            messages=recent_msgs_reversed,
        )

        # NOTE (Jonny): add in the last messages as a query too!
        # pull at most 2 messages
        token_budget = 128
        last_msgs: str = []
        for m in recent_msgs[:2]:
            token_budget -= self.clonedb.tokenizer.length(m.content) + 4
            if token_budget < 0:
                break
            last_msgs.append(m.content)
        last_msg = " ".join(reversed(last_msgs))
        if last_msg:
            queries.append(last_msg)
        else:
            logger.warning(
                f"Unable to use last messages for queries. Over token budget by {-token_budget}"
            )

        logger.info(f"Conversation ({self.conversation.id}) message queries: {queries}")
        return queries

    @tracer.start_as_current_span("generate_zero_memory_message")
    async def _generate_zero_memory_message(
        self, msg_gen: schemas.MessageGenerate
    ) -> models.Message:
        msg_to_unset: models.Message | None = None
        if msg_gen.is_revision:
            if not (last_messages := await self.clonedb.get_messages(num_messages=1)):
                raise HTTPException(
                    status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                    detail="There are no current messages in the conversation.",
                )
            msg_to_unset = last_messages[0]
            if not msg_to_unset.is_clone:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="Can only create a revision if the previous message was from the Clone.",
                )
            if msg_to_unset.parent_id is None:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="Revisions on the greeting message are not allowed.",
                )
        if self.information_strategy == InformationStrategy.internal:
            queries = await self._generate_msg_queries(
                num_messges=NUM_RECENT_MSGS_FOR_QUERY,
                num_tokens=int(0.66 * self.llm.context_length),
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
            vis: set[uuid.UUID] = set([])
            for q in queries:
                cur = await self.clonedb.query_nodes_with_rerank(
                    query=q, params=ReRankSearchParams(max_items=3, max_tokens=170)
                )
                for c in cur:
                    if c.model.id not in vis:
                        vis.add(c.model.id)
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
        tokens_remaining = self.llm.context_length
        tokens_remaining -= self.llm.num_tokens(cur_prompt)
        tokens_remaining -= generate.Params.generate_zero_memory_message.max_tokens

        recent_msgs = await self.clonedb.get_messages(num_tokens=tokens_remaining)
        if msg_to_unset:
            parent_id = msg_to_unset.parent_id
        else:
            parent_id = recent_msgs[0].id if recent_msgs else None

        messages = list(reversed(recent_msgs))

        # TODO (Jonny): it's possible that this thing spans multiple lines
        # so we need to return multiple messages
        new_msg_content = await generate.generate_zero_memory_message(
            char=self.clone.name,
            user_name=self.user_name,
            short_description=self.clone.short_description,
            long_description=self.clone.long_description,
            monologues=monologues,
            messages=messages,
            facts=facts,
            llm=self.llm,
            # TODO (Jonny): Figure out the use_timestamps logic here
        )
        content = remove_timestamps_from_msg(new_msg_content)
        new_msg_struct = Message(
            content=content,
            sender_name=self.clone.name,
            is_clone=True,
            parent_id=parent_id,
        )
        new_msg = await self.clonedb.add_message(new_msg_struct, msg_to_unset)

        return new_msg

    @tracer.start_as_current_span("generate_long_term_memory_message")
    async def _generate_long_term_memory_message(
        self, msg_gen: schemas.MessageGenerate
    ) -> models.Message:
        msg_to_unset: models.Message | None = None
        if msg_gen.is_revision:
            if not (last_messages := await self.clonedb.get_messages(num_messages=1)):
                raise HTTPException(
                    status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                    detail="There are no current messages in the conversation.",
                )
            msg_to_unset = last_messages[0]
            if not msg_to_unset.is_clone:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="Can only create a revision if the previous message was from the Clone.",
                )
            if msg_to_unset.parent_id is None:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="Revisions on the greeting message are not allowed.",
                )
        # short and long descriptions (max ~540 tokens)
        # (check generate.Params for more details)
        char = self.clone.name
        short_description = self.clone.short_description
        long_description = self.clone.long_description

        # generate the queries used for retrieval ops
        # since we don't have a user_message length cap, cutoff here
        queries = await self._generate_msg_queries(
            num_messges=NUM_RECENT_MSGS_FOR_QUERY,
            num_tokens=int(0.66 * self.llm.context_length),
        )
        mashed_query = " ".join(queries)

        # If we aren't using agent summaries and entity summaries,
        # that frees up ~1024 tokens, which we can use elsewhere. Figure
        # out if we have that space first!
        agent_summary: str | None = None
        entity_context_summary: str | None = None
        # this is the diff with short vs. long. short term just doesn't have adaptation.
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
                    raise HTTPException(
                        status_code=status.HTTP_400_BAD_REQUEST,
                        detail=f"Invalid adaptation strategy: {self.adaptation_strategy}",
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
            vis: set[uuid.UUID] = set()
            for q in queries:
                cur = await self.clonedb.query_nodes_with_rerank(
                    query=q,
                    params=ReRankSearchParams(max_items=3, max_tokens=fact_tokens),
                )
                for c in cur:
                    if c.model.id not in vis:
                        vis.add(c.model.id)
                        facts.append(c.model.content)

        # Retrieve relevant memories (max 512 tokens)
        memories: list[Memory] = []
        vis_mem: set[uuid.UUID] = set()
        for q in queries:
            cur = await self.clonedb.query_memories(
                q,
                params=GenAgentsSearchParams(max_tokens=memory_tokens, max_items=3),
                update_access_date=False,
            )
            for c in cur:
                if c.model.id not in vis_mem:
                    vis_mem.add(c.model.id)
                    mem = Memory(
                        id=c.model.id,
                        content=c.model.content,
                        timestamp=c.model.timestamp,
                        importance=c.model.importance,
                        is_shared=c.model.is_shared,
                    )
                    memories.append(mem)

        # we will prune overlapping memories with messages later, so this is a conservative
        # overcount early on in the convo
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
        tokens_remaining = self.llm.context_length
        tokens_remaining -= self.llm.num_tokens(cur_prompt)
        tokens_remaining -= generate.Params.generate_long_term_memory_message.max_tokens

        # we should have 4096 - (560_long + 250_mono + 300_fact + 300_mem)
        # - 512_gen - 1024_dyn ~ 1100 remaining for past messages.
        recent_msgs = await self.clonedb.get_messages(num_tokens=tokens_remaining)
        if msg_to_unset:
            parent_id = msg_to_unset.parent_id
        else:
            parent_id = recent_msgs[0].id if recent_msgs else None
        messages = list(reversed(recent_msgs))
        oldest_msg_timestamp = messages[0].timestamp

        # NOTE (Jonny): Since only shared memories can be non-messages at the moment,
        # we can just remove any memory that is more recent than the oldest message
        # and that is not shared. Pretty simple fix to prevent overlap. We also
        # allow reflections through, since they should not collide with memories either.
        memories = [
            m
            for m in memories
            if m.is_shared or m.depth > 0 or m.timestamp < oldest_msg_timestamp
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
        )
        content = remove_timestamps_from_msg(new_msg_content)
        new_msg_struct = Message(
            content=content,
            sender_name=self.clone.name,
            is_clone=True,
            parent_id=parent_id,
        )
        new_msg = await self.clonedb.add_message(new_msg_struct, msg_to_unset)
        mem_content = f'I messaged {self.user_name}, "{new_msg.content}"'
        # don't block on these
        self.background_tasks.add_task(self._add_private_memory, content=mem_content)
        return new_msg

    @tracer.start_as_current_span("generate_message")
    async def generate_message(
        self, msg_gen: schemas.MessageGenerate
    ) -> models.Message:
        """This method is the entire IP of this whole entire application, the goddamn GOAT.
        Calls all of the subroutines and returns the next message response for the clone.
        """
        # TODO (Jonny): Add a telemetry packet here with things like prompt size, n_msgs,
        # n_memories, n_pruned_memories, n_facts, fact_chars, mem_chars, etc.
        match self.memory_strategy:
            case MemoryStrategy.none:
                return await self._generate_zero_memory_message(msg_gen=msg_gen)
            case MemoryStrategy.short_term | MemoryStrategy.long_term:
                # the only diff is in adaptation strategy I guess, so it's
                # all just handled in the same function
                return await self._generate_long_term_memory_message(msg_gen=msg_gen)
            case _:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail=f"Invalid memory strategy: {self.memory_strategy}",
                )

    @tracer.start_as_current_span("generate_long_description")
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
        # TODO (Jonny): replace this with the real one, mock is too expensive
        import warnings

        from clonr.llms import MockLLM

        warnings.warn(
            "you hot swapped for a mock llm here. don't forget to change back"
        )

        long_desc = await generate.long_description_create(
            llm=MockLLM(), short_description=clone.short_description, docs=docs
        )
        # A stateful edit seems like a bad idea
        # clone.long_description = long_desc
        long_desc_model = models.LongDescription(
            content=long_desc, documents=docs, clone=clone
        )
        clonedb.db.add(long_desc_model)
        await clonedb.db.commit()
        await clonedb.db.refresh(long_desc_model, ["documents"])
        return long_desc_model
