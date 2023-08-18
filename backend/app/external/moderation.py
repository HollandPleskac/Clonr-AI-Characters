import logging

import aiohttp
from loguru import logger
from pydantic import BaseModel
from tenacity import after_log, before_sleep_log, retry, stop_after_attempt, wait_random

from app.settings import settings

OPENAI_MODERATION_URL = "https://api.openai.com/v1/moderations"


class ModerationResult(BaseModel):
    flagged: bool
    categories: dict[str, bool]
    category_scores: dict[str, float]


class ModerationResponse(BaseModel):
    id: str
    model: str
    results: list[ModerationResult]


@retry(
    stop=stop_after_attempt(3),
    wait=wait_random(min=0, max=1),
    before_sleep=before_sleep_log(logger, logging.INFO),  # type: ignore
    after=after_log(logger, logging.WARN),  # type: ignore
)
async def openai_moderation_check(text: str) -> ModerationResult:
    headers = {
        "Content-Type": "application/json",
        "Authorization": f"Bearer {settings.OPENAI_API_KEY}",
    }
    data = {"input": text}
    async with aiohttp.ClientSession(raise_for_status=True) as session:
        async with session.post(
            OPENAI_MODERATION_URL, headers=headers, json=data
        ) as response:
            response_data = await response.json()
    obj = ModerationResponse(**response_data)
    result = obj.results[0]
    return result
