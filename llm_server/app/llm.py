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

if settings.cache:
    cache = llama_cpp.LlamaCache(capacity_bytes=settings.cache_size)
    llm.set_cache(cache)


async def get_llm():
    with lock:
        yield llm
