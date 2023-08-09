import json
from abc import ABC, abstractmethod

import requests
from fastapi import status
from fastapi.exceptions import HTTPException
from loguru import logger
from sqlalchemy.ext.asyncio import AsyncSession

from app import models
from app.clone.cache import CloneCache
from app.external.moderation import openai_moderation_check
from clonr.llms.base import LLM
from clonr.llms.schemas import (
    GenerationParams,
    LLMResponse,
    Message,
    OpenAIStreamResponse,
)

# NOTE (Jonny): the **kwargs is really bad coding practice, but I could not find another solution
# I spent nearly a full day with codeblock on this. The issue, is that we want to trigger some event
# that occurs on every LLM call. We are solving this by adding a callback that you can add to an LLM
# at instantiation. This works so long as every argument that needs to go to the callback is either
# (a) available at callback instantiation (b) an output of the LLM call. However, the problem is that
# in some cases we need more. We need the name of the template used to generate the prompt (tells us
# what function is being read since the names are identical) and we need to know what subroutine is
# being run (for example, if we are processing a call during index construction, or during any of the multi-part
# processes like reflection generation.) The only solution I could find that both allows arbitrary functions
# to execute on LLM calls (like updating a db, or writing logs), does not face concurrency issues (
# if we write attributes on the LLM class we can read and write out of order!) is to prop drill with kwargs.
# Other solutions are to re-instantiate the LLM class at every turn, but that quickly runs into problems. Callbacks
# are not apriori composable. The kwargs solution allows the callback to make use of arbitrary keyword arguments
# and puts it on the user to make sure that they are passed down from the highest level to the LLM call.


class LLMCallback(ABC):
    @abstractmethod
    async def on_generate_start(
        self,
        llm: LLM,
        prompt_or_messages: str | list[Message],
        params: GenerationParams | None,
        **kwargs,
    ):
        pass

    @abstractmethod
    async def on_generate_end(self, llm: LLM, llm_response: LLMResponse, **kwargs):
        pass

    async def on_stream_start(
        self,
        llm: LLM,
        prompt_or_messages: str | list[Message],
        params: GenerationParams | None,
        **kwargs,
    ):
        pass

    async def on_token_received(self, llm: LLM, delta: OpenAIStreamResponse, **kwargs):
        pass

    async def on_stream_end(self, llm: LLM, **kwargs):
        pass

    async def check_moderation(self, text: str, api_key: str):
        headers = {
            "Content-Type": "application/json",
            "Authorization": f"Bearer {api_key}",
        }
        data = {"input": text}
        response = requests.post(
            "https://api.openai.com/v1/moderations", headers=headers, json=data
        )
        return response.json()


class LoggingCallback(LLMCallback):
    async def on_generate_start(
        self,
        llm: LLM,
        prompt_or_messages: str | list[Message],
        params: GenerationParams | None,
        **kwargs,
    ):
        try:
            # This will dump all of the extra arguments used, so we don't flood with prompts
            data = json.dumps(kwargs)
        except Exception as e:
            logger.error(e)
            data = ""
        response = await self.check_moderation(prompt_or_messages, llm.api_key)
        flagged = response.get("flagged", False)
        if flagged:
            raise ValueError("Flagged by moderation endpoint!")

        logger.info(f"LLM CALL START: {data}")

    async def on_generate_end(self, llm: LLM, llm_response: LLMResponse, **kwargs):
        try:
            info = json.dumps(kwargs)
        except Exception as e:
            logger.error(e)
            info = ""
        logger.info(
            (
                f"LLM CALL FINISH: Usage: {llm_response.usage.json()}. "
                f"Time: {llm_response.time:.02f}, {llm_response.tokens_per_second:.02f} tok/s. "
                f"Info: {info}"
            )
        )


# (Jonny): every LLMCall has a clone and user, but it might
# not have a conversation associated with it. The clone can be
# thought of as the creator, and the user as the consumer.


class AddToPostgresCallback(LLMCallback):
    def __init__(
        self,
        db: AsyncSession,
        clone_id: str,
        user_id: str,
        conversation_id: str | None = None,
    ):
        self.db = db
        self.clone_id = clone_id
        self.user_id = user_id
        self.conversation_id = conversation_id

    # (Jonny): sharing this callback between concurrent requests means that
    # we can't assign state in the callbacks so you can't communicate
    # information from here to on_generate_end
    async def on_generate_start(
        self,
        llm: LLM,
        prompt_or_messages: str | list[Message],
        params: GenerationParams | None,
        **kwargs,
    ):
        response = await self.check_moderation(prompt_or_messages, llm.api_key)
        flagged = response.get("flagged", False)
        if flagged:
            raise ValueError("Flagged by moderation endpoint!")

    async def on_generate_end(self, llm: LLM, llm_response: LLMResponse, **kwargs):
        r = llm_response
        mdl = models.LLMCall(
            model_type=r.model_type,
            model_name=r.model_name,
            prompt_tokens=r.usage.prompt_tokens,
            completion_tokens=r.usage.completion_tokens,
            total_tokens=r.usage.total_tokens,
            duration=r.duration,
            role=r.role,
            tokens_per_second=r.tokens_per_second,
            input_prompt=r.input_prompt,
            clone_id=self.clone_id,
            user_id=self.user_id,
            conversation_id=self.conversation_id,
            **kwargs,
        )
        self.db.add(mdl)
        await self.db.commit()


# TODO (Jonny): This probably should only run when receiving a message through
# our API. Revist whether we want to call this so frequently. Also, add additional
# logging (table?) to track what content we received that was flagged per user.
class ModerationCallback(LLMCallback):
    def __init__(
        self,
        db: AsyncSession,
        cache: CloneCache,
        clone_id: str,
        user_id: str,
        conversation_id: str | None = None,
    ):
        self.db = db
        self.cache = cache
        self.clone_id = clone_id
        self.user_id = user_id
        self.conversation_id = conversation_id

    async def on_generate_start(
        self,
        llm: LLM,
        prompt_or_messages: str | list[Message],
        params: GenerationParams | None,
        **kwargs,
    ):
        prompt = prompt_or_messages
        if not isinstance(prompt_or_messages, str):
            prompt = [x.to_str() for x in prompt_or_messages]
        response = await openai_moderation_check(prompt)
        if response.flagged:
            await self.increment_flagged_counter()
            for k, v in response.categories.items():
                if v:
                    raise HTTPException(
                        status_code=status.HTTP_400_BAD_REQUEST,
                        detail=f"Received content: ({prompt}) was marked as inappropriate. Reason: ({k})",
                    )

    async def increment_flagged_counter(self):
        await self.cache.add_moderation_violations(self.user_id)
