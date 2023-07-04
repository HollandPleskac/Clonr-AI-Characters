from pathlib import Path


def get_artifacts_dir() -> Path:
    path = Path(__file__).parent.parent.parent
    for _ in range(2):
        if (path / ".github").exists():
            return path / "artifacts"
        path = path.parent
    raise ValueError(f"We're not really at the root, we're at {path.resolve()}")


def get_transformers_dir() -> Path:
    return get_artifacts_dir() / "transformers"


def get_onnx_dir() -> Path:
    return get_artifacts_dir() / "onnx"
