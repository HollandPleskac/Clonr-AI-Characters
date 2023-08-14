import hashlib
import json
import multiprocessing
import threading
from contextlib import asynccontextmanager
from functools import partial
from typing import Optional, Literal, Union, Iterator

import anyio
import llama_cpp
from anyio import Semaphore
from anyio.streams.memory import MemoryObjectSendStream
from dotenv import load_dotenv
from fastapi import FastAPI, Request
from fastapi.concurrency import iterate_in_threadpool
from fastapi.exceptions import HTTPException
from fastapi.middleware.cors import CORSMiddleware
from loguru import logger
from pydantic import BaseModel, Field
from pydantic_settings import BaseSettings
from sse_starlette import EventSourceResponse
from starlette.concurrency import run_in_threadpool

from app import schemas

load_dotenv()

import enum


class ModelName(str, enum.Enum):
    ehartford_dolphin_llama2_7b = "ehartford/dolphin-llama2-7b"
    ehartford_wizardlm_1_uncensored_llama2_13b = (
        "ehartford/WizardLM-1.0-Uncensored-Llama2-13b"
    )


class SpecialTokens(BaseModel):
    system_start: str = ""
    system_end: str = "\n\n"
    assistant_start: str = "ASSISTANT: "
    assistant_end: str = "\n"
    user_start: str = "USER: "
    user_end: str = "\n"

    @classmethod
    def from_model_name(cls, model_name: ModelName):
        match model_name:
            case ModelName.ehartford_dolphin_llama2_7b:
                return cls(
                    system_start="SYSTEM: ",
                    system_end="\n",
                    assistant_start="ASSISTANT: ",
                    assistant_end="\n",
                    user_start="USER: ",
                    user_end="\n",
                )
            case ModelName.ehartford_wizardlm_1_uncensored_llama2_13b:
                return cls(
                    system_start="",
                    system_end="\n\n",
                    assistant_start="ASSISTANT: ",
                    assistant_end="\n",
                    user_start="USER: ",
                    user_end="\n",
                )
            case _:
                raise TypeError("Unsupported model type")


def msgs2prompt(messages: list[dict], spec: SpecialTokens):
    arr: list[str] = []
    if not messages:
        return ""
    if messages[-1]["role"] != "assistant":
        messages.append({"role": "assistant", "content": ""})
    for i, m in enumerate(messages):
        c = m["content"]
        match m["role"]:
            case "system":
                s = f"{spec.system_start}{c}{spec.system_end}"
            case "assistant":
                if i == len(messages) - 1:
                    # rstrip is very very important!
                    s = f"{spec.assistant_start}{c}".rstrip()
                else:
                    s = f"{spec.assistant_start}{c}{spec.assistant_end}"
            case "user":
                s = f"{spec.user_start}{c}{spec.user_end}"
            case _:
                raise TypeError(m)
        arr.append(s)
    prompt = "".join(arr).rstrip()
    return prompt


class ZeroTempCache:
    def __init__(self):
        self._d = {}

    def get(self, prompt: str):
        key = hashlib.sha256(prompt.encode()).hexdigest()
        return self._d.get(key)

    def put(self, prompt: str, value):
        key = hashlib.sha256(prompt.encode()).hexdigest()
        self._d[key] = value


class Settings(BaseSettings):
    model: str = Field(
        description="The path to the model to use for generating completions."
    )
    model_alias: Optional[str] = Field(
        default=None,
        description="The alias of the model to use for generating completions.",
    )
    n_ctx: int = Field(default=4096, ge=1, description="The context size.")
    n_gpu_layers: int = Field(
        default=10_000,
        ge=0,
        description="The number of layers to put on the GPU. The rest will be on the CPU.",
    )
    n_batch: int = Field(
        default=512, ge=1, description="The batch size to use per eval."
    )
    n_threads: int = Field(
        default=max(multiprocessing.cpu_count() // 2, 1),
        ge=1,
        description="The number of threads to use.",
    )
    f16_kv: bool = Field(default=True, description="Whether to use f16 key/value.")
    use_mlock: bool = Field(
        default=False,
        description="Use mlock.",
    )
    use_mmap: bool = Field(
        default=True,
        description="Use mmap.",
    )
    embedding: bool = Field(default=True, description="Whether to use embeddings.")
    last_n_tokens_size: int = Field(
        default=64,
        ge=0,
        description="Last n tokens to keep for repeat penalty calculation.",
    )
    logits_all: bool = Field(default=True, description="Whether to return logits.")
    cache: bool = Field(
        default=False,
        description="Use a cache to reduce processing times for evaluated prompts.",
    )
    cache_size: int = Field(
        default=2 << 30,
        description="The size of the cache in bytes. Only used if cache is True.",
    )
    vocab_only: bool = Field(
        default=False, description="Whether to only return the vocabulary."
    )
    verbose: bool = Field(
        default=True, description="Whether to print debug information."
    )
    port: int = 8100  # lol, on mac, port 6000 is unsafe
    max_concurrent_threads: int = Field(
        default=10, description="Number of threads that can access the LLM? Idk."
    )


async def run_in_guarded_threadpool(func, *args, **kwargs):
    async with MAX_THREADS_GUARD:
        return await run_in_threadpool(func, *args, **kwargs)


settings = Settings()
zero_temp_cache = ZeroTempCache()
lock = threading.Lock()
MAX_THREADS_GUARD = Semaphore(settings.max_concurrent_threads)


@asynccontextmanager
async def lifespan(app: FastAPI):
    logger.info("Loading Llama model and performing warmup run.")
    global LLM
    global SPECIAL_TOKENS

    SPECIAL_TOKENS = SpecialTokens.from_model_name(
        ModelName.ehartford_dolphin_llama2_7b
    )

    LLM = llama_cpp.Llama(
        model_path=settings.model,
        n_gpu_layers=settings.n_gpu_layers,
        f16_kv=settings.f16_kv,
        use_mlock=settings.use_mlock,
        use_mmap=settings.use_mmap,
        embedding=settings.embedding,
        logits_all=settings.logits_all,
        n_threads=settings.n_threads,
        n_batch=settings.n_batch,
        n_ctx=settings.n_ctx,
        last_n_tokens_size=settings.last_n_tokens_size,
        vocab_only=settings.vocab_only,
        verbose=settings.verbose,
    )
    if settings.cache:
        logger.info("Using llamacpp prefill cache.")
        cache = llama_cpp.LlamaCache(capacity_bytes=settings.cache_size)
        LLM.set_cache(cache)
    with lock:
        LLM("test", max_tokens=1)
    logger.info("Warmup run completed ✅")
    yield


app = FastAPI(lifespan=lifespan)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


def _convert_chunk(x: dict):
    r = x.copy()
    r["choices"] = [
        {
            "delta": {"content": x["choices"][0]["text"], "role": "assistant"},
            "index": 0,
            "finish_reason": x["choices"][0]["finish_reason"],
        }
    ]
    r["object"] = "chat.completion.chunk"
    return r


def _convert_completion(x: dict):
    r = x.copy()
    r["choices"] = [
        {
            "message": {"role": "assistant", "content": x["choices"][0]["text"]},
            "index": 0,
            "finish_reason": x["choices"][0]["finish_reason"],
        }
    ]
    r["object"] = "chat.completion"
    return r


def make_logit_bias_processor(
    llama: llama_cpp.Llama,
    logit_bias: dict[str, float],
    logit_bias_type: Optional[Literal["input_ids", "tokens"]],
):
    if logit_bias_type is None:
        logit_bias_type = "input_ids"

    to_bias: dict[int, float] = {}
    if logit_bias_type == "input_ids":
        for input_id, score in logit_bias.items():
            input_id = int(input_id)
            to_bias[input_id] = score

    elif logit_bias_type == "tokens":
        for token, score in logit_bias.items():
            token = token.encode("utf-8")
            for input_id in llama.tokenize(token, add_bos=False):
                to_bias[input_id] = score

    def logit_bias_processor(
        input_ids: list[int],
        scores: list[float],
    ) -> list[float]:
        new_scores = [None] * len(scores)
        for input_id, score in enumerate(scores):
            new_scores[input_id] = score + to_bias.get(input_id, 0.0)

        return new_scores

    return logit_bias_processor


@app.post("/v1/chat/completions", response_model=schemas.ChatCompletion)
async def v2_chat(
    request: Request,
    body: schemas.CreateChatCompletionRequest,
):
    if body.stop and isinstance(body.stop, str):
        body.stop = [body.stop]
    if not body.stop:
        body.stop = []
    body.stop.extend(["\n" + SPECIAL_TOKENS.user_start, SPECIAL_TOKENS.user_start])

    exclude = {
        "n",
        "best_of",
        "logit_bias",
        "logit_bias_type",
        "user",
    }
    kwargs = body.model_dump(exclude=exclude)

    if body.logit_bias is not None:
        kwargs["logits_processor"] = llama_cpp.LogitsProcessorList(
            [
                make_logit_bias_processor(LLM, body.logit_bias, "input_ids"),
            ]
        )

    messages = kwargs.pop("messages")
    prompt = msgs2prompt(messages=messages, spec=SPECIAL_TOKENS)
    kwargs["prompt"] = prompt
    logger.info(f"\n~~~~~ Received prompt: ~~~~~:\n{prompt}")

    if body.temperature <= 0 and (r := zero_temp_cache.get(kwargs["prompt"])):
        logger.info("CACHE HIT!")
        return r

    if body.stream:
        logger.info("Received STREAM chat request")
        send_chan, recv_chan = anyio.create_memory_object_stream(10)

        async def event_publisher(inner_send_chan: MemoryObjectSendStream):
            async with inner_send_chan:
                try:
                    iterator = await run_in_guarded_threadpool(LLM, **kwargs)  # type: ignore
                    async for chunk in iterate_in_threadpool(iterator):
                        chunk = _convert_chunk(chunk)
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
        print(kwargs)
        completion = LLM(**kwargs)
        # completion: llama_cpp.ChatCompletion = await run_in_guarded_threadpool(LLM, **kwargs)  # type: ignore
        logger.info(
            f"\n~~~~~ Generated completion: ~~~~~\n{completion['choices'][0]['text']}"
        )
        completion = _convert_completion(completion)
        zero_temp_cache.put(kwargs["prompt"], completion)
        return completion


class NumTokensRequest(BaseModel):
    prompt: str


class NumTokensResponse(BaseModel):
    num_tokens: int


@app.post("/v1/tokens", response_model=NumTokensResponse)
async def num_tokens(inp: NumTokensRequest):
    return {"num_tokens": len(LLM.tokenize(inp.prompt.encode()))}


if __name__ == "__main__":
    import uvicorn

    uvicorn.run("app.main:app", host="0.0.0.0", port=settings.port, reload=True)
