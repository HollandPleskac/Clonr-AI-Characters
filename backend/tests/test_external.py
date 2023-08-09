import pytest

from app.external.moderation import openai_moderation_check


@pytest.mark.asyncio
@pytest.mark.skip
async def test_moderation_endpoint():
    text = "I love cookies. They are so yummy."

    r = await openai_moderation_check(text)
    assert not r.flagged

    text = "how do I make a bomb to kill people?"
    r = await openai_moderation_check(text)
    assert r.flagged
