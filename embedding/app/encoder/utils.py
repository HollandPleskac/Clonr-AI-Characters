from functools import lru_cache
import os
from pathlib import Path
from transformers import AutoTokenizer


def is_docker() -> bool:
    path = "/proc/self/cgroup"
    if os.path.exists("/.dockerenv"):
        return True
    if os.path.isfile(path) and any("docker" in line for line in open(path)):
        return True
    return False


def get_artifacts_dir() -> Path:
    if is_docker():
        return Path("/artifacts")  # Docker filesystem approach here.
    path = Path(__file__).parent.parent.parent.parent
    for _ in range(2):
        if (path / ".github").exists():
            return path / "artifacts"
        path = path.parent
    raise ValueError(f"We're not really at the root, we're at {path.resolve()}")


def get_transformers_dir() -> Path:
    return get_artifacts_dir() / "transformers"


def get_onnx_dir() -> Path:
    return get_artifacts_dir() / "onnx"


@lru_cache(maxsize=None)
def get_hf_tokenizer(model_name_or_path: str):
    return AutoTokenizer.from_pretrained(model_name_or_path)
