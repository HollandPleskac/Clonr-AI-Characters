import json
from functools import partial

import anyio
import llama_cpp
from anyio.streams.memory import MemoryObjectSendStream
from fastapi import APIRouter, Depends, Request
from fastapi.concurrency import iterate_in_threadpool
from loguru import logger
from sse_starlette import EventSourceResponse

from app import schemas
from app.llm import get_llm
from app.utils import run_in_guarded_threadpool

router = APIRouter()

import time


@router.post(
    "/v1/completions",
    response_model=schemas.Completion,
)
async def create_completion(
    request: Request,
    body: schemas.CreateCompletionRequest,
    llama: llama_cpp.Llama = Depends(get_llm),
):
    if isinstance(body.prompt, list):
        assert len(body.prompt) <= 1
        body.prompt = body.prompt[0] if len(body.prompt) > 0 else ""

    exclude = {
        "n",
        "best_of",
        "logit_bias",
        "user",
    }
    kwargs = body.dict(exclude=exclude)
    if body.stream:
        send_chan, recv_chan = anyio.create_memory_object_stream(10)

        async def event_publisher(inner_send_chan: MemoryObjectSendStream):
            async with inner_send_chan:
                try:
                    iterator = await run_in_guarded_threadpool(llama, **kwargs)  # type: ignore
                    async for chunk in iterate_in_threadpool(iterator):
                        await inner_send_chan.send(dict(data=json.dumps(chunk)))
                        if await request.is_disconnected():
                            raise anyio.get_cancelled_exc_class()()
                    await inner_send_chan.send(dict(data="[DONE]"))
                except anyio.get_cancelled_exc_class() as e:
                    logger.exception("CreatCompletion disconnected")
                    with anyio.move_on_after(1, shield=True):
                        logger.exception(
                            f"Disconnected from client (via refresh/close) {request.client}"
                        )
                        await inner_send_chan.send(dict(closing=True))
                        raise e

        return EventSourceResponse(
            recv_chan, data_sender_callable=partial(event_publisher, send_chan)
        )
    else:
        completion: llama_cpp.Completion = await run_in_guarded_threadpool(llama, **kwargs)  # type: ignore
        return completion


@router.post(
    "/v1/chat",
    response_model=schemas.ChatCompletion,
)
async def create_chat_completion(
    request: Request,
    body: schemas.CreateChatCompletionRequest,
    llama: llama_cpp.Llama = Depends(get_llm),
):
    if body.stop and isinstance(body.stop, str):
        body.stop = [body.stop]
    exclude = {
        "n",
        "logit_bias",
        "user",
    }
    kwargs = body.dict(exclude=exclude)

    if body.stream:
        logger.info("Received STREAM chat request")
        send_chan, recv_chan = anyio.create_memory_object_stream(10)

        async def event_publisher(inner_send_chan: MemoryObjectSendStream):
            async with inner_send_chan:
                try:
                    iterator = await run_in_guarded_threadpool(llama.create_chat_completion, **kwargs)  # type: ignore
                    async for chat_chunk in iterate_in_threadpool(iterator):
                        await inner_send_chan.send(dict(data=json.dumps(chat_chunk)))
                        if await request.is_disconnected():
                            raise anyio.get_cancelled_exc_class()()
                    await inner_send_chan.send(dict(data="[DONE]"))
                except anyio.get_cancelled_exc_class() as e:
                    logger.exception("disconnected")
                    with anyio.move_on_after(1, shield=True):
                        logger.exception(
                            f"Disconnected from client (via refresh/close) {request.client}"
                        )
                        await inner_send_chan.send(dict(closing=True))
                        raise e

        return EventSourceResponse(
            recv_chan,
            data_sender_callable=partial(event_publisher, send_chan),
        )
    else:
        logger.info("Received NORMAL chat request")
        completion: llama_cpp.ChatCompletion = await run_in_guarded_threadpool(
            llama.create_chat_completion, **kwargs  # type: ignore
        )
        return completion


@router.post(
    "/v1/chat/mock",
    response_model=schemas.ChatCompletion,
)
async def create_mock_chat_completion(
    request: Request,
    body: schemas.CreateCompletionRequest,
):
    _mock_counter = time.time()

    msg = schemas.ChatCompletionMessage(
        role="assistant", content=f"Mock {_mock_counter}", user=None
    )
    choices = [schemas.ChatCompletionChoice(index=0, message=msg, finish_reason="stop")]
    usage = schemas.CompletionUsage(
        prompt_tokens=4, completion_tokens=4, total_tokens=4
    )
    r = schemas.ChatCompletion(
        id="mock-id",
        object="chat.completion",
        created=time.time(),
        model="mock",
        choices=choices,
        usage=usage,
    )
    return r


@router.post(
    "/v1/completions/mock",
    response_model=schemas.Completion,
)
async def create_mock_completion(
    request: Request,
    body: schemas.CreateCompletionRequest,
):
    _mock_counter = time.time()

    choices = [
        schemas.CompletionChoice(
            index=0, text=f"Mock {_mock_counter}", logprobs=None, finish_reason="stop"
        )
    ]
    usage = schemas.CompletionUsage(
        prompt_tokens=4, completion_tokens=4, total_tokens=4
    )
    r = schemas.Completion(
        id="mock-id",
        object="text_completion",
        created=time.time(),
        model="mock",
        choices=choices,
        usage=usage,
    )
    return r
