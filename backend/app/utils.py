import hashlib
import secrets
from pathlib import Path

from dateutil.parser import isoparse

# put this before all API keys so that we can use Github secret scanning
# https://docs.github.com/en/code-security/secret-scanning/about-secret-scanning
SECRET_PREFIX = "cz3k_"


def iso2unix(s: str):
    return isoparse(s).timestamp()


def get_local_data_dir() -> Path:
    return Path(__file__).parent.parent / "_data"


def get_voice_data_dir():
    return get_local_data_dir() / "audio"


def generate_api_key():
    return SECRET_PREFIX + secrets.token_urlsafe(48)


def sha256_hash(x: str):
    return hashlib.sha256(x.encode()).hexdigest()
