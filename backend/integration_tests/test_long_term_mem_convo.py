import time

import sqlalchemy as sa
from fastapi.encoders import jsonable_encoder
from fastapi.testclient import TestClient
from loguru import logger
from sqlalchemy.orm import Session

from app import models, schemas
from app.clone.controller import (
    AGENT_SUMMARY_THRESHOLD,
    ENTITY_CONTEXT_THRESHOLD,
    NUM_REFLECTION_MEMORIES,
)
from app.clone.types import AdaptationStrategy, InformationStrategy, MemoryStrategy


def test_long_term_memory_convo(
    client: TestClient, user_headers: dict[str, str], makima_id: str, db: Session
):
    # Create a conversation as User
    user_name = "Jonny"
    convo_create = schemas.ConversationCreate(
        clone_id=makima_id,
        user_name=user_name,
        memory_strategy=MemoryStrategy.long_term,
        information_strategy=InformationStrategy.internal,
        adaptation_strategy=AdaptationStrategy.moderate,
    )
    req_data = jsonable_encoder(convo_create)
    r = client.post("/conversations/", json=req_data, headers=user_headers)
    data = r.json()
    assert r.status_code == 201, data
    convo_id = data["id"]

    # Alternate adding a user message and generating a clone message
    # do this like 200 times to make sure that
    # (a) tokens don't overflow
    # (b) reflections are generated at some point
    # the mock importance is 4, so reflections should trigger after about 20 messages
    is_clone = False
    count = 0
    start_time = time.time()
    N = 15
    fake_msgs = [
        "hey whats up??? just checkin in, wanted to see wussup witchu nahhhh. " * 4,
        "你这个哦周末干什么? 我们去公园怎么样我们去公园怎么样. " * 4,
        "whatchu doin this weekend? ngl finna get turnt, no cap. " * 4,
        "お前はキモイね 👋 私に話しかけないでください. " * 4,
    ]
    num_greeting_msgs = 1
    tot_msgs = N * len(fake_msgs) + num_greeting_msgs
    for _ in range(N):
        for content in fake_msgs:
            print("Message:", count)
            if is_clone:
                r = client.post(
                    f"/conversations/{convo_id}/generate",
                    json=dict(is_revision=False),
                    headers=user_headers,
                )
                data = r.json()
                assert r.status_code == 201, data
                assert data["is_clone"] and data["is_main"] and data["is_active"]
            else:
                msg_create = schemas.MessageCreate(content=content)
                r = client.post(
                    f"/conversations/{convo_id}/messages",
                    json=msg_create.model_dump(),
                    headers=user_headers,
                )
                data = r.json()
                assert r.status_code == 201, data
                assert not data["is_clone"] and data["is_main"] and data["is_active"]
            count += 1
            if not count % 10:
                logger.info(
                    f"Msg {count}/{N * len(fake_msgs)} completed. {1e3 * (time.time()-start_time) / count:.02f}ms / msg."
                )
            is_clone = not is_clone

    avg = sa.func.sum(models.LLMCall.prompt_tokens) / sa.func.count(models.LLMCall.id)
    max_len = sa.func.max(models.LLMCall.prompt_tokens)
    min_len = sa.func.min(models.LLMCall.prompt_tokens)
    count = sa.func.count(models.LLMCall.id)
    stats = db.execute(sa.select(avg, max_len, min_len, count))
    d = dict(zip(["avg", "max", "min", "count"], stats.first()))
    s = " ".join(f"{k}: {v:.02f}." for k, v in d.items())

    print("STATISTICS:", s)

    # check that we logged at least one memory for each message + the greeting
    memories = db.query(models.Memory).all()
    assert len(memories) >= tot_msgs

    # check that no prompts went over the max allowed value
    n_violations = db.scalar(
        sa.select(sa.func.count(models.LLMCall.id)).where(
            models.LLMCall.prompt_tokens > 3800
        )
    )
    assert not n_violations, n_violations

    # check that we've triggered reflections
    # mock llm is built-in importance of 4
    n_reflections = ((tot_msgs - 1) * 4) // NUM_REFLECTION_MEMORIES
    n_refl_obs = db.scalar(
        sa.select(sa.func.count(models.Memory.id))
        .where(models.Memory.depth > 0)
        .where(models.Memory.conversation_id == convo_id)
    )
    assert n_refl_obs == n_reflections

    # check that we've triggered agent_summaries
    # mock llm is built-in importance of 4
    expected = ((tot_msgs - 1) * 4) // AGENT_SUMMARY_THRESHOLD
    computed = db.scalar(
        sa.select(sa.func.count(models.AgentSummary.id)).where(
            models.AgentSummary.conversation_id == convo_id
        )
    )
    assert expected == computed

    # check that we've triggered entity_context_summaries
    # mock llm is built-in importance of 4
    expected = ((tot_msgs - 1) * 4) // ENTITY_CONTEXT_THRESHOLD
    computed = db.scalar(
        sa.select(sa.func.count(models.EntityContextSummary.id)).where(
            models.EntityContextSummary.conversation_id == convo_id
        )
    )
    assert expected == computed
