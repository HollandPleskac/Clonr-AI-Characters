from typing import Annotated

from fastapi import Depends, Path
from sqlalchemy.ext.asyncio import AsyncSession

from app.settings import settings
from clonr.llms import LLM, LlamaCpp, MockLLM, OpenAI
from clonr.llms.callbacks import AddToPostgresCallback, LLMCallback, LoggingCallback
from clonr.tokenizer import Tokenizer

from .db import get_async_session
from .text import get_tokenizer
from .users import get_current_active_user


# no auth done here, it's assumed to have been done in the clonedb
async def get_llm(
    db: Annotated[AsyncSession, Depends(get_async_session)],
    clone_id: Annotated[str, Path()],
    user: Annotated[str, Depends(get_current_active_user)],
    tokenizer: Annotated[Tokenizer, Depends(get_tokenizer)],
    conversation_id: Annotated[str | None, Path()] = None,
) -> LLM:
    callbacks: list[LLMCallback] = [
        LoggingCallback(),
        AddToPostgresCallback(
            db=db, clone_id=clone_id, user_id=user.id, conversation_id=conversation_id
        ),
    ]
    if settings.LLM == "mock":
        llm = MockLLM(callbacks=callbacks)
    elif settings.LLM == "llamacpp":
        llm = LlamaCpp(chat_mode=True)
    else:
        llm = OpenAI(
            model=settings.LLM,
            api_key=settings.OPENAI_API_KEY,
            tokenizer=tokenizer,
            callbacks=callbacks,
        )
    yield llm
