from typing import Annotated

from fastapi import Depends, Path, status
from fastapi.exceptions import HTTPException
from redis.asyncio import Redis
from sqlalchemy.ext.asyncio import AsyncSession

from app import models
from app.auth.users import current_active_creator, current_active_user
from app.clone.cache import CloneCache
from app.clone.db import CloneDB
from app.db import get_async_redis, get_async_session
from app.embedding import EmbeddingClient, get_embedding_client
from app.settings import settings
from clonr.index import Index, ListIndex
from clonr.llms import LLM, MockLLM, OpenAI
from clonr.text_splitters import DynamicTextSplitter, SentenceSplitter, TokenSplitter
from clonr.tokenizer import Tokenizer

if settings.LLM == "mock":
    TOKENIZER = Tokenizer.from_openai("gpt-3.5-turbo")
    llm = MockLLM()
else:
    TOKENIZER = Tokenizer.from_openai(settings.LLM)
    llm = OpenAI(
        model=settings.LLM, api_key=settings.OPENAI_API_KEY, tokenizer=TOKENIZER
    )

# TODO (Jonny): make these passable by environment variables?
# Currently we are just using the default settings in text_splitters.py
# @dataclass
# class DEFAULTS:
#     max_chunk_size_chars: int = 512
#     min_chunk_size_chars: int = 64
#     max_chunk_size_tokens: int = 128
#     min_chunk_size_tokens: int = 16
#     overlap_chars: int = 128
#     overlap_tokens: int = 32

dynamic_splitter = DynamicTextSplitter(
    sentence_splitter=SentenceSplitter(tokenizer=TOKENIZER, use_tokens=True),
    token_splitter=TokenSplitter(
        tokenizer=TOKENIZER,
    ),
)


async def get_splitter() -> DynamicTextSplitter:
    yield dynamic_splitter


async def get_tokenizer() -> Tokenizer:
    yield TOKENIZER


async def get_llm() -> LLM:
    yield llm


async def get_clone_model_as_creator(
    db: Annotated[AsyncSession, Depends(get_async_session)],
    clone_id: Annotated[str, Path(min_length=36, max_length=36)],
    user: Annotated[str, Depends(current_active_user)],
) -> models.Clone:
    if clone := await db.get(models.Clone, clone_id):
        if user.id == clone.creator_id or user.is_superuser:
            yield clone
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN)
    else:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Clone id ({clone_id}) not found.",
        )


async def get_clonedb(
    clone_model: Annotated[models.Clone, Depends(get_clone_model_as_creator)],
    db: Annotated[AsyncSession, Depends(get_async_session)],
    conn: Annotated[Redis, Depends(get_async_redis)],
    tokenizer: Annotated[Tokenizer, Depends(get_tokenizer)],
    embedding_client: Annotated[EmbeddingClient, Depends(get_embedding_client)],
    conversation_id: Annotated[str | None, Path(min_length=36, max_length=36)] = None,
) -> CloneDB:
    cache = CloneCache(conn=conn)
    clonedb = CloneDB(
        db=db,
        cache=cache,
        tokenizer=tokenizer,
        embedding_client=embedding_client,
        clone_id=clone_model.clone_id,
        conversation_id=conversation_id,
    )
    yield clonedb


# # llm is not needed for the basic list index! We can revisit TreeIndex in the future
# # but for now, it's too much complexity for a yet to be demonstrated reward
# async def get_index(
#     tokenizer: Annotated[Tokenizer, Depends(get_tokenizer)],
#     splitter: Annotated[DynamicTextSplitter, Depends(get_splitter)],
#     # embedding_client: Annotated[EmbeddingClient, Depends(get_embedding_client)],
# ) -> Index:
#     index = ListIndex(tokenizer=tokenizer, splitter=splitter)
#     yield index
