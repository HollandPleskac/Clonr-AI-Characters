from functools import lru_cache
from pathlib import Path


@lru_cache(maxsize=None)
def load_lebron_data():
    path = Path(__file__).parent / "assets" / "lebron-wiki.txt"
    with open(path, "r") as f:
        return f.read()


@lru_cache(maxsize=None)
def load_paul_graham_data():
    path = Path(__file__).parent / "assets" / "paul-graham-essay.txt"
    with open(path, "r") as f:
        return f.read()


@lru_cache(maxsize=None)
def load_makima_data():
    path = Path(__file__).parent / "assets" / "makima.txt"
    with open(path, "r") as f:
        return f.read()
