from pathlib import Path

from .formatting import bytes_to_human_readable
from .hf_downloader import HFDownloader


def get_artifacts_dir() -> Path:
    path = Path(__file__).parent.parent.parent.parent
    if not (path / ".github").exists():
        raise ValueError(f"We're not really at the root, we're at {path.resolve()}")
    return path / "artifacts"
