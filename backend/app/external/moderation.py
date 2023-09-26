import logging
from contextlib import nullcontext

import aiohttp
import requests
from loguru import logger
from pydantic import BaseModel
from tenacity import (
    after_log,
    before_sleep_log,
    retry,
    stop_after_attempt,
    wait_exponential,
)

from app.settings import settings

OPENAI_MODERATION_URL = "https://api.openai.com/v1/moderations"


class bcolors:
    HEADER = "\033[95m"
    OKBLUE = "\033[94m"
    OKCYAN = "\033[96m"
    OKGREEN = "\033[92m"
    WARNING = "\033[93m"
    FAIL = "\033[91m"
    ENDC = "\033[0m"
    BOLD = "\033[1m"
    UNDERLINE = "\033[4m"


class ModerationResult(BaseModel):
    flagged: bool
    categories: dict[str, bool]
    category_scores: dict[str, float]

    def __repr__(self):
        if self.flagged:
            flagged = f"{bcolors.FAIL}unsafe{bcolors.ENDC}"
            flags_arr = [""] + [
                f"{k}={100 * v:.02f}"
                for k, v in self.category_scores.items()
                if self.categories[k]
            ]
            flags = ", ".join(flags_arr)
        else:
            flagged = f"{bcolors.OKGREEN}safe{bcolors.ENDC}"
            k, v = max(self.category_scores.items(), key=lambda x: x[1])
            flags = f", {k}={100 * v:.02f}"
        return f"{self.__class__.__name__}({flagged}{flags})"

    def top_category(self) -> tuple[str, float]:
        return max(self.category_scores.items(), key=lambda x: x[1])


class ModerationResponse(BaseModel):
    id: str
    model: str
    results: list[ModerationResult]


@retry(
    stop=stop_after_attempt(6),
    wait=wait_exponential(),
    before_sleep=before_sleep_log(logger, logging.INFO),  # type: ignore
    after=after_log(logger, logging.WARN),  # type: ignore
)
async def openai_moderation_check(
    text: str, api_key: str | None = None, session: aiohttp.ClientSession | None = None
) -> ModerationResult:
    headers = {
        "Content-Type": "application/json",
        "Authorization": f"Bearer {api_key or settings.OPENAI_API_KEY}",
    }
    data = {"input": text}
    async with (
        nullcontext(session)
        if session
        else aiohttp.ClientSession(raise_for_status=True) as session
    ):
        async with session.post(
            OPENAI_MODERATION_URL, headers=headers, json=data
        ) as response:
            response_data = await response.json()
    obj = ModerationResponse(**response_data)
    result = obj.results[0]
    return result


@retry(
    stop=stop_after_attempt(6),
    wait=wait_exponential(),
    before_sleep=before_sleep_log(logger, logging.INFO),  # type: ignore
    after=after_log(logger, logging.WARN),  # type: ignore
)
def openai_moderation_check_synchronous(
    text: str, api_key: str | None = None
) -> ModerationResult:
    headers = {
        "Content-Type": "application/json",
        "Authorization": f"Bearer {api_key or settings.OPENAI_API_KEY}",
    }
    data = {"input": text}
    response = requests.post(OPENAI_MODERATION_URL, headers=headers, json=data)
    response.raise_for_status()
    response_data = response.json()
    obj = ModerationResponse(**response_data)
    result = obj.results[0]
    return result
