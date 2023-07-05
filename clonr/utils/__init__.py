from datetime import datetime
from pathlib import Path
from typing import Callable, TypeVar
from zoneinfo import ZoneInfo

from .formatting import bytes_to_human_readable
from .hf_downloader import HFDownloader
from .paths import get_artifacts_dir, get_onnx_dir, get_transformers_dir

T = TypeVar("T")


def get_current_datetime(
    include_seconds: bool = True, tz: str | ZoneInfo = ZoneInfo("utc")
) -> datetime:
    """Timezone stuff can get tricky. Machine local time is ZoneInfo('localtime'). The ZoneInfo
    library is part of the standard library as of Python 3.9+. Other timezone examples are
    US/Pacific, US/Eastern, US/Central
    https://stackoverflow.com/questions/10997577/python-timezone-conversion

    Args:
        include_seconds (bool, optional): whether to add seconds. Defaults to True.
        tz (str | ZoneInfo, optional): which timezone to use. Defaults to ZoneInfo('utc').

    Returns:
        datetime: Python datetime object in the proper timezone
    """
    if isinstance(tz, str):
        tz = ZoneInfo(tz)
    return datetime.now(tz=tz)


def convert_timezone(dt: datetime, tz: str | ZoneInfo) -> datetime:
    if isinstance(tz, str):
        tz = ZoneInfo(tz)
    return dt.astimezone(tz=tz)


def aggregate_by_length(
    arr: list[T], max_size: int, length_fn: Callable[[T], int]
) -> list[list[T]]:
    if len(arr) <= 1:
        return arr
    res: list[list[T]] = []
    cur: list[T] = []
    size = 0
    for x in arr:
        el = length_fn(x)
        if not cur or (size + el) <= max_size:
            cur.append(x)
            size += el
        else:
            res.append(cur)
            cur = [x]
            size = el
    if cur:
        res.append(cur)
    return res
