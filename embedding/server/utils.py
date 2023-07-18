from pathlib import Path
from functools import lru_cache

from transformers import AutoTokenizer


def get_artifacts_dir() -> Path:
    path = Path(__file__).parent.parent.parent
    for _ in range(2):
        if (path / ".github").exists():
            return path / "artifacts"
        path = path.parent
    raise ValueError(f"We're not really at the root, we're at {path.resolve()}")


@lru_cache(maxsize=None)
def get_hf_tokenizer(model_name_or_path: str):
    return AutoTokenizer.from_pretrained(model_name_or_path)
