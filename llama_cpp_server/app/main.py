import hashlib
import json
import multiprocessing
import re
import threading
import time
from contextlib import asynccontextmanager
from dataclasses import dataclass
from functools import partial
from typing import Optional

import anyio
import guidance
import llama_cpp
import torch
from anyio import Semaphore
from anyio.streams.memory import MemoryObjectSendStream
from app import schemas
from dotenv import load_dotenv
from fastapi import FastAPI, Request
from fastapi.concurrency import iterate_in_threadpool
from fastapi.exceptions import HTTPException
from fastapi.middleware.cors import CORSMiddleware
from loguru import logger
from pydantic import BaseModel, BaseSettings, Field
from sse_starlette import EventSourceResponse
from starlette.concurrency import run_in_threadpool
from transformers import LlamaTokenizer

load_dotenv()


class ZeroTempCache:
    def __init__(self):
        self._d = {}

    def get(self, prompt: str):
        key = hashlib.sha256(prompt.encode()).hexdigest()
        return self._d.get(key)

    def put(self, prompt: str, value):
        key = hashlib.sha256(prompt.encode()).hexdigest()
        self._d[key] = value


zero_temp_cache = ZeroTempCache()


class Settings(BaseSettings):
    model: str = Field(
        description="The path to the model to use for generating completions."
    )
    model_alias: Optional[str] = Field(
        default=None,
        description="The alias of the model to use for generating completions.",
    )
    n_ctx: int = Field(default=2048, ge=1, description="The context size.")
    n_gpu_layers: int = Field(
        default=0,
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
    port: int = 6000
    max_concurrent_threads: int = Field(
        default=10, description="Number of threads that can access the LLM? Idk."
    )


@dataclass
class _InnerModelConfig:
    vocab_size: int
    max_sequence_length: int
    pad_token_id: int | None


class _InnerModel:
    def __init__(self, model):
        self.model = model
        for k, v in vars(model).items():
            if k != "generate":
                setattr(self, k, v)

    def to(self):
        return self

    @property
    def device(self):
        return None

    @property
    def config(self):
        return _InnerModelConfig(
            vocab_size=llama_cpp.llama_n_vocab(self.ctx),
            max_sequence_length=self.params.n_ctx,
            pad_token_id=None,
        )

    def generate(self, inputs, **kwargs):
        kwargs["inputs"] = inputs
        gen = self.model.generate(
            tokens=inputs[0],
            temp=kwargs["temperature"],
            top_p=kwargs["top_p"],
            logits_processor=kwargs["logits_processor"],
            stopping_criteria=kwargs["stopping_criteria"],
        )
        d = {"sequences": [], "scores": []}
        if streamer := kwargs.get("streamer"):
            streamer.put({"sequences": inputs})
        for i, token in enumerate(gen):
            d["sequences"].append(token)
            d["scores"].append(self.eval_logits[-1])
            if streamer:
                streamer.put(
                    {k: torch.tensor(v[-1:]).reshape(1, -1) for k, v in d.items()}
                )
            if i > kwargs["max_new_tokens"]:
                break
        if streamer:
            streamer.end()
        return {
            "sequences": torch.tensor(d["sequences"]),
            "scores": torch.tensor(d["scores"])[None],
        }


class GuidanceLLM(guidance.llms._transformers.Transformers):
    def __init__(self, model, **kwargs):
        self.model = model
        tokenizer = LlamaTokenizer.from_pretrained("openlm-research/open_llama_7b")
        return super().__init__(
            model=model,
            tokenizer=tokenizer,
            acceleration=False,
            caching=False,
            **kwargs,
        )


settings = Settings()
lock = threading.Lock()

MAX_THREADS_GUARD = Semaphore(settings.max_concurrent_threads)


async def run_in_guarded_threadpool(func, *args, **kwargs):
    async with MAX_THREADS_GUARD:
        return await run_in_threadpool(func, *args, **kwargs)


@asynccontextmanager
async def lifespan(app: FastAPI):
    logger.info("Loading Llama model and performing warmup run.")
    global LLM
    global GUIDANCE_LLM
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
        cache = llama_cpp.LlamaCache(capacity_bytes=settings.cache_size)
        LLM.set_cache(cache)
    GUIDANCE_LLM = GuidanceLLM(model=_InnerModel(LLM))
    with lock:
        LLM("test", max_tokens=1)
    logger.info("Warmup run completed ✅")
    yield


app = FastAPI(title="llama.cpp server", version="0.0.1", lifespan=lifespan)

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


@app.post("/v1/chat/completions", response_model=schemas.ChatCompletion)
async def v2_chat(
    request: Request,
    body: schemas.CreateChatCompletionRequest,
):
    if body.stop and isinstance(body.stop, str):
        body.stop = [body.stop]

    if body.logit_bias is None:
        body.logit_bias = {}

    exclude = {
        "n",
        "logit_bias",
        "user",
    }
    kwargs = body.dict(exclude=exclude)

    # if bias := kwargs.pop("logit_bias"):
    #     logger.error(f"Received bias: {bias}")

    #     def _bias_fn(arr):
    #         for k, v in bias.items():
    #             arr[k] += v
    #         return arr

    #     kwargs["logits_processor"] = [_bias_fn]

    print(json.dumps(kwargs, indent=2))

    messages = kwargs.pop("messages")
    # WARNING. We concatenate with a newline. This might be an unexpected prompt adjustment from the user side!
    prompt = "\n".join([x["content"] for x in messages])
    logger.info(f"Received prompt: {prompt}")
    kwargs["prompt"] = messages[0]["content"]

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
        completion: llama_cpp.ChatCompletion = await run_in_guarded_threadpool(LLM, **kwargs)  # type: ignore
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


class GuidanceRequest(BaseModel):
    prompt: str
    variables: dict | None = None

    class Config:
        schema_extra = {
            "example": {
                "prompt": 'When in the course of{{gen "response" max_tokens=16 temperature=0.7}}',
                "variables": {},
            }
        }


class GuidanceResponse(BaseModel):
    text: str
    variables: dict
    input_tokens: int
    completion_tokens: int
    total_tokens: int
    generation_time: float
    tokens_per_second: float


@app.post("/v1/guidance", response_model=GuidanceResponse)
async def guidance_completion(
    body: GuidanceRequest,
):
    st = time.time()
    if body.variables is None:
        body.variables = {}
    program = guidance(body.prompt, async_mode=True, silent=True)
    r = await program(llm=GUIDANCE_LLM, **body.variables)

    variables = r.variables()
    variables.pop("llm")

    # This can break for a bunch of reasons, but none of it really matters
    # since llama cpp sucks, it can only do gen. Error causes would be using
    # the hidden function, things like select or if statements
    completion_tokens = 0
    for k, v in variables.items():
        if k not in body.variables:
            completion_tokens += len(GUIDANCE_LLM.encode(v))
    total_tokens = len(GUIDANCE_LLM.encode(r.text))
    input_tokens = total_tokens - completion_tokens

    return GuidanceResponse(
        text=r.text,
        variables=variables,
        input_tokens=input_tokens,
        completion_tokens=completion_tokens,
        total_tokens=total_tokens,
        generation_time=time.time() - st,
        tokens_per_second=total_tokens / (time.time() - st),
    )


if __name__ == "__main__":
    import uvicorn

    uvicorn.run("app.main:app", host="0.0.0.0", port=settings.port, reload=True)
