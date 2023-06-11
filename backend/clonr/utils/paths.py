from pathlib import Path

def get_artifacts_dir() -> Path:
    path = Path(__file__).parent.parent.parent.parent
    if not (path / ".github").exists():
        raise ValueError(f"We're not really at the root, we're at {path.resolve()}")
    return path / "artifacts"


def get_onnx_dir() -> Path:
    return get_artifacts_dir() / "onnx"