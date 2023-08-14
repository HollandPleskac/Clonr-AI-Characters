import os
import uuid
from typing import Annotated

import sqlalchemy as sa
from fastapi import Depends, Path
from sqlalchemy.ext.asyncio import AsyncSession

from app import models
from app.settings import settings
from clonr.llms import LLM, LlamaCpp, MockLLM, OpenAI
from clonr.llms.callbacks import AddToPostgresCallback, LLMCallback, LoggingCallback
from clonr.tokenizer import Tokenizer

from .db import get_async_session
from .text import get_tokenizer
from .users import get_current_active_user


def is_docker() -> bool:
    path = "/proc/self/cgroup"
    if os.path.exists("/.dockerenv"):
        return True
    if os.path.isfile(path) and any("docker" in line for line in open(path)):
        return True
    return False


def _get_llm(
    model_name: str, tokenizer: Tokenizer, callbacks: list[LLMCallback]
) -> LLM:
    if model_name == "mock":
        llm = MockLLM(callbacks=callbacks)
    elif model_name == "llamacpp":
        model = model_name
        if is_docker():
            # https://stackoverflow.com/questions/24319662/from-inside-of-a-docker-container-how-do-i-connect-to-the-localhost-of-the-mach
            # If we are running llama cpp locally, localhost won't work from inside the container.
            api_base = "http://host.docker.internal:8100/v1"
        else:
            api_base = "http://localhost:8100/v1"
    elif model_name == "colab":
        api_base = "<NGROK URL HERE>/v1"
        model = "<MODEL NAME HERE. MUST ALIGN WITH SERVER>"
        # model = "wizardlm-1.0-uncensored-llama2-13b"
        llm = LlamaCpp(
            model=model,
            api_base=api_base,
            api_key="none",
            tokenizer=tokenizer,
            callbacks=callbacks,
        )
    elif model_name.startswith("gpt"):
        llm = OpenAI(
            model=model_name,
            api_key=settings.OPENAI_API_KEY,
            tokenizer=tokenizer,
            callbacks=callbacks,
        )
    else:
        raise ValueError("Invalid model name:" + model_name)
    return llm


# no auth done here, it's assumed to have been done in the clonedb
async def get_llm_with_convo_id(
    db: Annotated[AsyncSession, Depends(get_async_session)],
    clone_id: Annotated[uuid.UUID | None, Path()],
    user: Annotated[str, Depends(get_current_active_user)],
    tokenizer: Annotated[Tokenizer, Depends(get_tokenizer)],
    conversation_id: Annotated[uuid.UUID, Path()],
) -> LLM:
    if clone_id is None:
        clone_id = await db.scalar(
            sa.select(models.Conversation.clone_id).where(
                models.Conversation.id == conversation_id
            )
        )
    callbacks: list[LLMCallback] = [
        LoggingCallback(),
        AddToPostgresCallback(
            db=db, clone_id=clone_id, user_id=user.id, conversation_id=conversation_id
        ),
    ]
    llm = _get_llm(model_name=settings.LLM, tokenizer=tokenizer, callbacks=callbacks)
    yield llm


async def get_llm_with_clone_id(
    db: Annotated[AsyncSession, Depends(get_async_session)],
    clone_id: Annotated[uuid.UUID, Path()],
    user: Annotated[str, Depends(get_current_active_user)],
    tokenizer: Annotated[Tokenizer, Depends(get_tokenizer)],
) -> LLM:
    callbacks: list[LLMCallback] = [
        LoggingCallback(),
        AddToPostgresCallback(
            db=db, clone_id=clone_id, user_id=user.id, conversation_id=None
        ),
    ]
    llm = _get_llm(model_name=settings.LLM, tokenizer=tokenizer, callbacks=callbacks)
    yield llm
