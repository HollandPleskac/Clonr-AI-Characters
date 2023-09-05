import hashlib
import secrets
from pathlib import Path
from functools import lru_cache

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


def _get_removal_index(s1: str, s2: str) -> int | None:
    candidates = {}
    for i, x in enumerate(s1):
        if x == s2[0]:
            candidates[i] = 0
        for k in list(candidates):
            if candidates[k] >= len(s2):
                candidates.pop(k)
            elif x == s2[candidates[k]]:
                candidates[k] += 1
            else:
                candidates.pop(k)
    if candidates:
        return min(candidates)


def remove_overlaps_in_list_of_strings(arr: list[str]) -> list[str]:
    """Removes overlapping elements from a list of strings.
    This is useful for removing redundant elements from adjacent
    retrieved chunks. Given strings ['ABC', 'CDE', 'DEFG'], this would
    return ['AB', 'C', 'DEFG']

    Args:
        arr (list[str]): an array of strings with potential overlaps

    Returns:
        list[str]: deduplicated array
    """
    arr = arr.copy()
    if len(arr) <= 1:
        return arr
    for i in range(len(arr) - 1, 0, -1):
        if (idx := _get_removal_index(arr[i - 1], arr[i])) is not None:
            if idx <= 0:
                arr.pop(i - 1)
            else:
                arr[i - 1] = arr[i - 1][:idx]
    return arr


@lru_cache()
def calc_likes_z(confidence):
    import scipy.stats as st

    return st.norm.ppf(1 - (1 - confidence) / 2)


# https://www.evanmiller.org/how-not-to-sort-by-average-rating.html
def likes_score(pos, n, confidence=0.95):
    """Used for ranking items that have likes and dislikes"""
    import math

    if n <= 0:
        return 0
    z = calc_likes_z(confidence)
    p = pos / n
    lower_bound = (
        p + z**2 / (2 * n) - z * math.sqrt((p * (1 - p) + z**2 / (4 * n)) / n)
    ) / (1 + z**2 / n)
    return lower_bound


# https://www.evanmiller.org/ranking-items-with-star-ratings.html#changes
def ratings_rank_score(scores: list[int], K: int, confidence: float = 0.95):
    """Used for rankings items that have a history rankings. scores is the list of ratings
    for this item. K is the max score allowed (i.e. 5 on a 1-5 star rating system)
    The last factor z is computed as"""
    assert K > 0, "ratings must be from 1 -> K"
    import numpy as np

    z = calc_likes_z(confidence)
    nk = np.bincount(np.array(scores) - 1, minlength=K)
    sk = np.arange(1, K + 1)
    N = len(scores)
    bias = sk @ ((nk + 1) / (N + K))
    v1 = np.square(sk) @ ((nk + 1) / (N + K))
    v2 = np.square(bias)
    variance = -z * np.sqrt(((v1 - v2) / (N + K + 1)))
    return bias + variance
