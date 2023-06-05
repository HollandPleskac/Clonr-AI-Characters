from threading import Lock

import llama_cpp

from app.settings import settings

lock = Lock()

llm = llama_cpp.Llama(
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


def monkey_path_chat_completion(obj):
    def fn(
        messages,
        temperature: float = 0.2,
        top_p: float = 0.95,
        top_k: int = 40,
        stream: bool = False,
        stop=[],
        max_tokens: int = 256,
        presence_penalty: float = 0.0,
        frequency_penalty: float = 0.0,
        repeat_penalty: float = 1.1,
        tfs_z: float = 1.0,
        mirostat_mode: int = 0,
        mirostat_tau: float = 5.0,
        mirostat_eta: float = 0.1,
        model=None,
        user_token: str = "\n### Human: ",
        assistant_token: str = "\n### Assistant:",
    ):
        """Generate a chat completion from a list of messages.

        Args:
            messages: A list of messages to generate a response for.
            temperature: The temperature to use for sampling.
            top_p: The top-p value to use for sampling.
            top_k: The top-k value to use for sampling.
            stream: Whether to stream the results.
            stop: A list of strings to stop generation when encountered.
            max_tokens: The maximum number of tokens to generate.
            repeat_penalty: The penalty to apply to repeated tokens.

        Returns:
            Generated chat completion or a stream of chat completion chunks.
        """
        stop = (
            stop if isinstance(stop, list) else [stop] if isinstance(stop, str) else []
        )
        # TODO: this token stuff is not ideal. I guess it has to be built in since this is all done
        # server-side.
        chat_history = "".join(
            f"{user_token if message['role'] == 'user' else (assistant_token.rstrip() + ' ')}{message['content']}"
            for message in messages
        )
        if messages and messages[-1]["role"] == "assistant":
            PROMPT = chat_history
        else:
            PROMPT = chat_history + assistant_token
        print("prompt:", PROMPT)
        PROMPT_STOP = [assistant_token, user_token]
        completion_or_chunks = obj(
            prompt=PROMPT,
            stop=PROMPT_STOP + stop,
            temperature=temperature,
            top_p=top_p,
            top_k=top_k,
            stream=stream,
            max_tokens=max_tokens,
            repeat_penalty=repeat_penalty,
            presence_penalty=presence_penalty,
            frequency_penalty=frequency_penalty,
            tfs_z=tfs_z,
            mirostat_mode=mirostat_mode,
            mirostat_tau=mirostat_tau,
            mirostat_eta=mirostat_eta,
            model=model,
        )
        if stream:
            chunks = completion_or_chunks  # type: ignore
            return obj._convert_text_completion_chunks_to_chat(chunks)
        else:
            completion = completion_or_chunks  # type: ignore
            return obj._convert_text_completion_to_chat(completion)

    return fn


llm.create_chat_completion = monkey_path_chat_completion(llm)

if settings.cache:
    cache = llama_cpp.LlamaCache(capacity_bytes=settings.cache_size)
    llm.set_cache(cache)


async def get_llm():
    with lock:
        yield llm
