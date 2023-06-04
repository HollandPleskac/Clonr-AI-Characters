from pathlib import Path
from typing import Callable, TypeVar

from anyio import Semaphore
from starlette.concurrency import run_in_threadpool
from typing_extensions import ParamSpec

MAX_CONCURRENT_THREADS = 10
MAX_THREADS_GUARD = Semaphore(MAX_CONCURRENT_THREADS)
T = TypeVar("T")
P = ParamSpec("P")


async def run_in_guarded_threadpool(
    func: Callable[P, T], *args: P.args, **kwargs: P.kwargs
) -> T:
    async with MAX_THREADS_GUARD:
        return await run_in_threadpool(func, *args, **kwargs)


def get_model_dir() -> Path:
    return Path(__file__).parent.parent / "models"


def get_model_path(s: str):
    return str((get_model_dir() / s).resolve())
