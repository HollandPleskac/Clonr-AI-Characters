import secrets
from pathlib import Path

from dateutil.parser import isoparse


def iso2unix(s: str):
    return isoparse(s).timestamp()


def get_local_data_dir() -> Path:
    return Path(__file__).parent.parent / "_data"


def get_voice_data_dir():
    return get_local_data_dir() / "audio"


def generate_api_key():
    return secrets.token_urlsafe(50)
