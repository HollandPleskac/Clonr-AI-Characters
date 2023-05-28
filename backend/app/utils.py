from pathlib import Path


def get_local_data_dir() -> Path:
    return Path(__file__).parent.parent / "_data"


def get_voice_data_dir():
    return get_local_data_dir() / "audio"
