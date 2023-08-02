import json
from abc import ABC, abstractmethod
from typing import Any

from loguru import logger

from clonr.llms.base import LLM
from clonr.llms.schemas import GenerationParams, LLMResponse, Message

from .base import LLM
from .schemas import GenerationParams, LLMResponse, Message, OpenAIStreamResponse

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


class LoggingCallback(LLMCallback):
    async def on_generate_start(
        self,
        llm: LLM,
        prompt_or_messages: str | list[Message],
        params: GenerationParams | None,
        **kwargs,
    ):
        try:
            data = json.dumps(kwargs)
        except Exception as e:
            logger.error(e)
            data = ""
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
                f"Duration: {llm_response.duration:.02f}, {llm_response.tokens_per_second:.02f} tok/s. "
                f"Info: {info}"
            )
        )
