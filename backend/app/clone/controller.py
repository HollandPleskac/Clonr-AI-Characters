from pydantic import BaseModel
from redis.asyncio import Redis
from sqlalchemy.ext.asyncio import AsyncSession

from app import models, schemas
from app.clone.types import AdaptationStrategy, MemoryStrategy
from app.embedding import EmbeddingClient
from clonr import generate
from clonr.data_structures import Memory, Message
from clonr.llms import LLM
from clonr.tokenizer import Tokenizer

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


class Thresholds(BaseModel):
    reflection: int
    entity_context: int
    agent_summary: int

    @classmethod
    def from_plasticity(cls, plasticity: int):
        if plasticity < 0 or plasticity > 10:
            raise ValueError(f"Plasticity must be between 0-10. Received {plasticity}")


class Controller:
    def __init__(
        self,
        llm: LLM,
        clonedb: CloneDB,
        clone: models.Clone,
        conversation: models.Conversation,
    ):
        self.llm = llm
        self.clonedb = clonedb
        self.clone = clone
        self.conversation = conversation

    @property
    def memory_strategy(self) -> schemas.MemoryStrategy:
        return self.conversation.memory_strategy

    @property
    def information_strategy(self) -> schemas.InformationStrategy:
        return self.conversation.information_strategy

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
        )
        await clonedb.add_message(greeting_message)

        return convo

    async def _add_memory(self, content: str):
        importance = generate.rate_memory(llm=self.llm, memory=content)

        await self.db.increment_reflection_counter(importance=importance)
        await self.db.increment_agent_summary_counter(importance=importance)
        await self.db.increment_entity_context_counter(importance=importance)

        memory = Memory(content=content, importance=importance)

    async def receive_message(self, msg_create: schemas.MessageCreate):
        data = msg_create.dict(exclude_unset=True)
        sender_name = self.user_name
        msg_struct = Message(sender_name=sender_name, is_clone=False, **data)
        msg = await self.db.add_message(msg_struct)

        if self.memory_strategy == schemas.MemoryStrategy.advanced:
            f'{self.user_name} messaged me, "{msg.content}"'
            await self.add_memory(memory)

        # trigger any needed summarizations
        if await self.db.get_reflection_count() > REFLECTION_THRESHOLD:
            await self.reflect()
            await self.db.set_reflection_count(0)

        if await self.db.get_entity_context_count() > ENTITY_CONTEXT_THRESHOLD:
            # TODO (Jonny): something is missing here, how do we feed the info for entity context summaries?
            query = "???"
            statements = self.db.query_memories(
                query=query, params=GenAgentsSearchParams(max_items=30)
            )
            await generate.entity_context_create(
                llm=self.llm,
                char=self.clone.name,
                entity=ENTITY_NAME,
                statements=statements,
            )
            await self.db.set_entity_context_count(0)

        if await self.db.get_agent_summary_count() > AGENT_SUMMARY_THRESHOLD:
            # TODO (Jonny): something is broken here too, how do we feed the info for agent summaries?
            await self.db.set_agent_summary_count(0)


# TODO (Jonny): This is the main logic class and still very much a WIP
# The constructor needs settings corresponding to the various levels of memory complexity
# like short-term, long-term, external api, information retrieval, multi-character, planning, ...
# class Controller:
#     def __init__(
#         self,
#         clonedb: CloneDB,
#         conversation: models.Conversation,
#     ):
#         self.clonedb = clonedb
#         self.conversation = conversation

#     @classmethod
#     async def create_conversation(cls, ):
#         # Initialize counters
#         await self.db.set_reflection_count(0)
#         await self.db.set_agent_summary_count(0)
#         await self.db.set_entity_context_count(0)

#         # add seed memories
#         seed_memories = [
#             Memory(content="I started a conversation with {ENTITY_NAME}", importance=4)
#         ]
#         await self.db.add_memories(seed_memories)
#         logger.info(
#             f"Clone ({self.db.clone_id}) added seed memories ({seed_memories}) to conversation ({convo.id})."
#         )

#         # add greeting message
#         greeting_message = [
#             Message(
#                 content=self.clone.greeting_message,
#                 is_clone=True,
#                 sender_name=self.clone.name,
#             )
#         ]
#         await self.db.add_message(greeting_message)
#         logger.info(
#             f"Clone ({self.db.clone_id}) added greeting messsage ({greeting_message}) to conversation ({convo.id})."
#         )

#         logger.info(
#             f"Clone ({self.db.clone_id}) finished creating new conversation ({convo.id})."
#         )

# async def add_document_from_url(self, url: str):
#     doc = url_to_doc(url=url)
#     nodes = self.index.abuild(doc=doc)
#     await self.db.add_document(doc=doc, nodes=nodes)

# async def add_monologues_from_wikiquotes(self, url: str):
#     parser = WikiquoteParser()
#     monologues = parser.extract(url=url)
#     await self.db.add_monologues(monologues=monologues)

# async def add_memory(self, content: str):
#     importance = generate.rate_memory(llm=self.llm, memory=content)

#     # increment counters
#     await self.db.increment_reflection_counter(importance=importance)
#     await self.db.increment_agent_summary_counter(importance=importance)
#     # TODO (Jonny): we probably need some other kind of check for when this triggers
#     await self.db.increment_entity_context_counter(importance=importance)

#     # add memory to stream
#     memory = Memory(content=content, importance=importance)

# async def reflect(
#     self, num_memories: int | None = None, num_tokens: int | None = None
# ):
#     memories = await self.db.get_memories(
#         num_messages=num_memories, num_tokens=num_tokens
#     )
#     queries = generate.reflection_queries_create(llm=self.llm, memories=memories)
#     params = GenAgentsSearchParams(max_items=15)
#     retrieved_memories: list[models.Memory] = []
#     for q in queries:
#         cur = await self.db.query_memories(query=q, params=params)
#         retrieved_memories.extend(cur)
#     retrieved_memories.sort(key=lambda x: x.timestamp)
#     reflections = await generate.reflections_create(
#         llm=self.llm, memories=retrieved_memories
#     )
#     await self.db.add_memories(reflections)
#     await self.db.set_reflection_count(0)

# async def generate_long_description(self):
#     # TODO (Jonny): need a method to pull all documents related to a clone
#     docs = await self.db.get_documents(...)
#     long_desc = await generate.long_description_create(
#         llm=self.llm, short_description=self.clone.short_description, docs=docs
#     )
#     # Fuck do we need versioning here? what if they have multiple copies of something, also it's expensive AF to
#     # generate a long description, we should be conscious here
#     # TODO (Jonny): finish this shit
#     self.clone.long_description = long_desc
#     # we don't have access to a db though, ugh...
#     self.db.add(self.clone)
#     self.db.commit()

# async def receive_message(self, content: str, entity_name: str):
#     # add the actual message
#     msg = Message(content=content, sender_name=entity_name, is_clone=False)
#     await self.db.add_message(msg)

#     # add the formed memory
#     memory = f'{entity_name} messaged me, "{msg.content}"'
#     await self.add_memory(memory)

#     # trigger any needed summarizations
#     if await self.db.get_reflection_count() > REFLECTION_THRESHOLD:
#         await self.reflect()
#         await self.db.set_reflection_count(0)

#     if await self.db.get_entity_context_count() > ENTITY_CONTEXT_THRESHOLD:
#         # TODO (Jonny): something is missing here, how do we feed the info for entity context summaries?
#         query = "???"
#         statements = self.db.query_memories(
#             query=query, params=GenAgentsSearchParams(max_items=30)
#         )
#         await generate.entity_context_create(
#             llm=self.llm,
#             char=self.clone.name,
#             entity=ENTITY_NAME,
#             statements=statements,
#         )
#         await self.db.set_entity_context_count(0)

#     if await self.db.get_agent_summary_count() > AGENT_SUMMARY_THRESHOLD:
#         # TODO (Jonny): something is broken here too, how do we feed the info for agent summaries?
#         await self.db.set_agent_summary_count(0)

# async def create_response(self):
#     # The main method of the entire goddamn application. GOAt
#     # TODO (Jonny): add the num_messages and num_tokens to receive here
#     msgs = self.db.get_messages(num_messages=num_messages, num_tokens=num_tokens)
#     agent_summary = self.db.get_agent_summary()[0]
#     # TODO (Jonny): entity name is fucking things up
#     entity_name = "???"
#     entity_context_summary = self.db.get_entity_context_summary(
#         entity_name=entity_name
#     )
#     query = await generate.message_queries_create(
#         llm=self.llm,
#         char=self.clone.name,
#         short_description=self.clone.short_description,
#         agent_summary=agent_summary,
#         entity_context_summary=entity_context_summary,
#         entity_name=entity_name,
#         messages=msgs,
#     )

#     nodes = []
#     monologues = []
#     # TODO (Jonny): add some kind of filter to not retrieve memories whose content is
#     # already in the recent message stream?
#     memories = []
#     for q in query:
#         # TODO (Jonny): set the rerank params here too
#         cur = await self.db.query_nodes_with_rerank(
#             query=q, params=ReRankSearchParams()
#         )
#         nodes.extend(cur)
#         # TODO (Jonny): set the params for rerank here too
#         cur = await self.db.query_monologues_with_rerank(
#             query=q, params=ReRankSearchParams()
#         )
#         monologues.extend(cur)
#         # TODO (Jonny): set the params for gen agents search here too
#         cur = await self.db.query_memories(query=q, params=GenAgentsSearchParams())
#         memories.extend(cur)

#     # TODO (Jonny): lol wtf, where is the message generation function. literally the most important thing
#     response = await generate.response_create(
#         char=self.clone.name,
#         short_description=self.clone.short_description,
#         long_description=self.clone.long_description,
#         example_dialogues=monologues,
#         agent_summary=agent_summary,
#         memories=memories,
#         entity_context_summary=entity_context_summary,
#         entity_name=entity_name,
#         messages=messages,
#         nodes=nodes,
#     )

#     response_msg = Message(
#         content=response, sender_name=self.clone.name, is_clone=True
#     )
#     await self.db.add_message(response_msg)

#     return response_msg
