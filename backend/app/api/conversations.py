from typing import Annotated

from app import models, schemas
from app.auth.api_keys import get_api_key
from app.auth.users import current_active_user
from app.db import RedisCache, get_async_redis_cache, get_async_session
from fastapi import Depends, FastAPI
from fastapi import Depends, HTTPException, status
from fastapi.routing import APIRouter
from fastapi.encoders import jsonable_encoder
from fastapi import Request
from sqlalchemy import delete, select, update
from sqlalchemy.ext.asyncio import AsyncSession
import sqlalchemy as sa
from loguru import logger
from slowapi import Limiter

# from app.embedding import embed
from clonr.llms import LLM
from app.main import TOKENIZER
from app.character import (
    CHAR,
    EXAMPLE_DIALOGUES,
    INITIAL_MESSAGE,
    USER,
    create_message_query,
    create_prompt,
)

limiter = Limiter(default_limits=["5/minute"])


def calculate_dynamic_rate_limit(request: Request):
    print("TODO")
    return "5/minute"


router = APIRouter(
    prefix="/conversations",
    tags=["conversations"],
    responses={404: {"description": "Not found"}},
)


@router.post("/", response_model=schemas.Conversation)
async def create_conversation(
    obj: schemas.ConversationCreate,
    db: Annotated[AsyncSession, Depends(get_async_session)],
    cache: Annotated[RedisCache, Depends(get_async_redis_cache)],
    api_key: Annotated[schemas.APIKey, Depends(get_api_key)],
):
    clone = await db.get(models.Clone, api_key.clone_id)
    if not clone:
        raise HTTPException(
            status_code=400, detail="Clone corresponding to this key does not exist"
        )
    conversation = models.Conversation(**obj.dict())
    msg = models.Message(
        content=clone.greeting_message,
        sender_name=clone.name,
        from_clone=True,
        conversation=conversation,
    )
    db.add_all([msg, conversation])
    await db.commit()
    await db.refresh(conversation)
    await cache.message_add(msg)
    return conversation


@router.post("/{conversation_id}/messages", response_model=schemas.Message)
async def create_message(
    conversation_id: str,
    message: schemas.MessageCreate,
    db: Annotated[AsyncSession, Depends(get_async_session)],
    api_key: Annotated[schemas.APIKey, Depends(get_api_key)],
    cache: Annotated[RedisCache, Depends(get_async_redis_cache)],
):
    if not (convo := await db.get(models.Conversation, conversation_id)):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, detail="Conversation not found"
        )
    if api_key.clone_id != convo.clone_id:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Forbidden")
    msg = models.Message(
        **message.dict(), from_clone=False, conversation_id=conversation_id
    )
    db.add(msg)
    await db.commit()
    await db.flush(msg)
    await cache.message_add(msg)
    return msg


@router.get("/", response_model=list[schemas.Conversation])
async def get_conversations(
    db: Annotated[AsyncSession, Depends(get_async_session)],
    api_key: Annotated[schemas.APIKey, Depends(get_api_key)],
):
    promise = await db.scalars(
        select(models.Conversation).where(
            models.Conversation.clone_id == api_key.clone_id
        )
    )
    return promise.all()


# TODO: revisit this endpoint. Users should be able to access conversations
# using both API Key and user credentials. At the moment, we're only offering
# one or the other. OR maybe not idk. maybe we make this a security thing where
# API Keys completely control their conversations and all that
@router.get("/{conversation_id}", response_model=schemas.Conversation)
async def get_conversation(
    conversation_id: str,
    db: Annotated[AsyncSession, Depends(get_async_session)],
    api_key: Annotated[schemas.APIKey, Depends(get_api_key)],
):
    if not (convo := await db.get(models.Conversation, conversation_id)):
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Not found")
    if api_key.clone_id == convo.clone_id:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Not found")
    return convo


@router.get("/{conversation_id}/messages", response_model=list[schemas.Message])
async def get_latest_messages(
    conversation_id: str,
    db: Annotated[AsyncSession, Depends(get_async_session)],
    api_key: Annotated[schemas.APIKey, Depends(get_api_key)],
    cache: Annotated[RedisCache, Depends(get_async_redis_cache)],
    offset: int = 0,
    limit: int = 25,
):
    if not (convo := await db.get(models.Conversation, conversation_id)):
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Not found")
    if api_key.clone_id != convo.clone_id:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Not found")
    # TODO: This blocks access to our DB since we likely won't have cache misses
    # Becomes problematic once our cache fills up! Also the FIFO eviction policy should
    # be in place
    messages = await cache.message_get_latest(convo.id, offset=offset, limit=limit)
    if messages:
        return messages
    promise = await db.scalars(
        select(models.Message)
        .where(models.Message.conversation_id == id)
        .order_by(models.Message.created_at.desc())
        .offset(offset)
        .limit(limit)
    )
    messages = promise.all()
    return messages


@router.delete("/{id}", response_model=schemas.Conversation)
async def delete_conversation(
    id: str,
    db: Annotated[AsyncSession, Depends(get_async_session)],
    cache: Annotated[RedisCache, Depends(get_async_redis_cache)],
    api_key: Annotated[schemas.APIKey, Depends(get_api_key)],
):
    if not (convo := db.get(models.Conversation, id)):
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Not found")
    if api_key.clone_id != convo.clone_id:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Not found")
    await cache.conversation_delete(convo.id)
    await db.delete(convo)
    await db.commit()
    return convo


@router.delete(
    "/{conversation_id}/messages/{message_id}", response_model=schemas.Conversation
)
async def delete_message(
    request: Request,
    conversation_id: str,
    message_id: str,
    db: Annotated[AsyncSession, Depends(get_async_session)],
    cache: Annotated[RedisCache, Depends(get_async_redis_cache)],
    api_key: Annotated[schemas.APIKey, Depends(get_api_key)],
):
    if not (convo := await db.get(models.Conversation, conversation_id)):
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Not found")
    if not (msg := await db.get(models.Message, message_id)):
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Not found")
    if api_key.clone_id != convo.clone_id or msg.conversation_id != conversation_id:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Not found")
    await cache.message_delete(conversation_id=conversation_id, message_id=message_id)
    await db.delete(convo)
    await db.commit()
    return convo


@router.get("/v1/conversation/{convo_id}/response")
@limiter.limit(calculate_dynamic_rate_limit)
async def get_response(
    convo_id: str,
    db: Annotated[AsyncSession, Depends(get_async_session)],
    cache: Annotated[RedisCache, Depends(get_async_redis_cache)],
):
    # Retreive the past messages
    logger.info("Retrieving current coversation")
    current_message_token_lim = 1600
    current_messages: list[models.Message] = []
    q = await db.scalars(
        sa.select(models.Message)
        .where(models.Message.conversation_id == convo_id)
        .order_by(models.Message.timestamp.desc())
    )
    for msg in q:
        current_message_token_lim -= len(TOKENIZER.encode(msg.content)) + 3
        if current_message_token_lim >= 0:
            current_messages.append(msg)
        else:
            break
    # because latest is the first element and out prompt does '\n'.join
    current_messages = list(reversed(current_messages))
    logger.info(f"Retrieved: {len(current_messages)} messages")

    # create query for the past
    logger.info("Using last 6 messages to construct a DB query")
    queries = await create_message_query(llm=LLM, db=db, messages=current_messages[-6:])
    if queries is None:
        logger.error("\n Queries is None")
        queries = []
    logger.info("Retrieving similar records to query from DB")
    facts_: list[models.Chunk] = []
    past_messages_: list[models.Message] = []
    # embeddings = embed(queries)
    embeddings = []
    for e in embeddings:
        if f := (
            await db.scalars(
                sa.select(models.Chunk)
                .order_by(models.Chunk.embedding.cosine_distance(e))
                .limit(3)
            )
        ).all():
            facts_.extend(f)
        if p := (
            await db.scalars(
                sa.select(models.Message)
                .where(models.Message.conversation_id == convo_id)
                .order_by(models.Message.embedding.cosine_distance(e))
                .limit(3)
            )
        ).all():
            past_messages_.extend(p)
    vis = set(str(x.id) for x in current_messages)
    # logger.info(f"\n-----\n\n\nRELEVANT PAST MESSAGES:\n{past_messages_}\n\n\n------\n")
    past_messages_ = [x for x in past_messages_ if str(x.id) not in vis]

    fact_token_limit = 256
    facts = []
    for f in facts_:
        fact_token_limit -= len(TOKENIZER.encode(f.content))
        if fact_token_limit >= 0:
            facts.append(f)
        else:
            break

    past_message_token_limit = 128
    past_messages = []
    for f in past_messages_:
        past_message_token_limit -= len(TOKENIZER.encode(f.content))
        if past_message_token_limit >= 0:
            past_messages.append(f)
        else:
            break

    logger.info("Constructing Message prompt")
    prompt = create_prompt(
        facts=[x.content for x in facts],
        past_msgs=past_messages,
        current_msgs=current_messages,
    )
    logger.info("LLM call for message")
    r = await LLM.agenerate(prompt)
    msg = models.Message(
        sender_name=CHAR,
        content=r.content,
        embedding=embed(r.content)[0],
        conversation_id=convo_id,
    )
    # add to redis cache
    await cache.message_add(convo_id, msg)
    db.add(msg)
    llm_call = models.LLMCall(
        content=r.content,
        prompt_tokens=r.usage.prompt_tokens,
        completion_tokens=r.usage.completion_tokens,
        total_tokens=r.usage.total_tokens,
        finish_reason=r.finish_reason,
        role=r.role,
        tokens_per_second=r.tokens_per_second,
        prompt=prompt,
    )
    db.add(llm_call)
    await db.commit()
    response = jsonable_encoder(r)
    return response
