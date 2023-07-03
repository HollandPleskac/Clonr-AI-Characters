import os

import requests
from dotenv import load_dotenv

# from fastapi.encoders import jsonable_encoder
from sqlalchemy import select

from clonr.clone import Clone, AuthenticatedDB
from app.db import get_async_session
from clonr.llms import MockLLM
from clonr.embedding.encoder import EmbeddingModel
import transformers
import asyncio
import numpy as np
import datetime
import json

load_dotenv()


home = "http://localhost:8000"
register_url = os.path.join(home, "auth/register")
jwt_url = os.path.join(home, "auth/jwt/login")


def authenticate_user(email, password):
    with requests.session() as sess:
        r = sess.post(
            jwt_url,
            data=dict(
                username=email,
                password=password,
            ),
        )
        auth_header = {"Authorization": "Bearer " + r.json()["access_token"]}
        sess.headers.update(auth_header)

        r = sess.get(os.path.join(home, "users/me"))
        user = r.json()
        print("user_id:", user["id"], "\n-----\n")

        return sess, user


def create_clone(session, user_id):
    print("Creating a Clone")
    r = session.post(
        os.path.join(home, "clones"),
        json={
            "greeting_message": "Hi!",
            "name": "Makima",
            "description": "test",
            "motivation": "test",
            "user_id": user_id,
        },
    )
    clone_id = r.json()["id"]
    print("clone_id:", clone_id, "\n-----\n")
    return clone_id


def create_api_key(session, user_id, clone_id):
    print("Creating an API key")
    r = session.post(
        os.path.join(home, "api_keys"),
        json={"user_id": user_id, "clone_id": clone_id},
    )
    api_key = r.json()["key"]
    print("api_key:", api_key, "\n-----\n")
    return api_key


def create_conversation(session, clone_id):
    r = session.post(
        os.path.join(home, "conversations"),
        json=dict(name="Makima-convo-1", clone_id=clone_id),
    )
    convo_id = r.json()["id"]
    print("convo_id:", convo_id, "\n-----\n")
    return convo_id


def write_messages(session, convo_id):
    print("Writing some Messages")
    for msg in ["Hey Makima!", "Whats uppp?"]:
        session.post(
            os.path.join(home, "conversations", convo_id, "messages"),
            json=dict(content=msg, sender_name="Bob"),
        )
    r = session.get(os.path.join(home, "conversations", convo_id, "messages"))
    messages = r.json()
    print("messages:", messages, "\n-----\n")
    return


def create_memory(memory_json):
    print("Creating a Memory")
    r = session.post(
        os.path.join(home, "memories"),
        json=memory_json,
    )
    memory = r.json()
    print("memory:", memory, "\n-----\n")
    return memory


def get_memories(session, convo_id):
    # TODO
    print("Getting memories: ")
    r = session.get(os.path.join(home, "memories", "conversation", convo_id))
    memories = r.json()
    print("memories:", memories, "\n-----\n")
    return memories


async def test_clone(clone_id, user_id, api_key, conversation_id, session):
    print("testing clone..")
    db = AuthenticatedDB(
        session=session,
        clone_id=clone_id,
        api_key=api_key,
        user_id=user_id,
        conversation_id=conversation_id,
    )
    print("got db..")
    llm = MockLLM()
    print("got llm..")
    model = transformers.AutoModel.from_pretrained("intfloat/e5-small-v2")
    tokenizer = transformers.AutoTokenizer.from_pretrained("intfloat/e5-small-v2")
    embedding_model = EmbeddingModel(model=model, tokenizer=tokenizer)
    print("got embedding model..")
    clone = Clone(db=db, llm=llm, embedding_model=embedding_model)
    print("got clone..")
    memories = await clone.get_memories()
    print("initial memories: ", memories)
    # observation = "this is a test memory"
    # clone.create_memory(observation)
    # print("created memory..")
    # memories = clone.get_memories()
    # print("updated memories: ", memories)
    # latest_memories = clone.get_latest_memories()
    # print("latest memories: ", latest_memories)
    return


# def test_clone_full(clone_id, user_id, api_key, conversation_id):
#     await test_clone(clone_id, user_id, api_key, conversation_id)


if __name__ == "__main__":
    email = os.environ["SUPERUSER_EMAIL"]
    password = os.environ["SUPERUSER_PASSWORD"]
    session, user = authenticate_user(email, password)
    clone_id = create_clone(session, user["id"])
    print("this is clone_id:", clone_id)
    api_key = create_api_key(session, user["id"], clone_id)
    session.headers.update({"CLONR_API_KEY": api_key})
    convo_id = create_conversation(session, clone_id)
    print("this is convo_id: ", convo_id)
    memory_json = {
        "memory": "this is a test memory",
        "memory_embedding": [1.02, 2.03, 3.04],
        "timestamp": datetime.datetime.now().isoformat(),
        "last_accessed_at": datetime.datetime.now().isoformat(),
        "importance": 0.1,
        "is_shared": False,
        "is_reflection": False,
        "conversation_id": convo_id,
        "clone_id": clone_id,
    }
    print(json.dumps(memory_json, indent=4))
    create_memory(memory_json)
    # async_session = asyncio.run(get_async_session().__anext__())
    # asyncio.run(test_clone(clone_id, user["id"], api_key, convo_id, async_session))


# if __name__ == "__main__":
#     with requests.session() as sess:
#         print("Grabbing JWT")
#         r = sess.post(
#             jwt_url,
#             data=dict(
#                 username=os.environ["SUPERUSER_EMAIL"],
#                 password=os.environ["SUPERUSER_PASSWORD"],
#             ),
#         )
#         auth_header = {"Authorization": "Bearer " + r.json()["access_token"]}
#         sess.headers.update(auth_header)

#         print("Getting my own credentials")
#         r = sess.get(os.path.join(home, "users/me"))
#         user = r.json()
#         print("user_id:", user["id"], "\n-----\n")

#         print("Creating a Clone")
#         r = sess.post(
#             os.path.join(home, "clones"),
#             json={
#                 "greeting_message": "Hi!",
#                 "name": "Makima",
#                 "description": "test",
#                 "motivation": "test",
#             },
#         )
#         print(r.json())
#         clone_id = r.json()["id"]
#         print("clone_id:", clone_id, "\n-----\n")
#         r = sess.get(os.path.join(home, "clones", clone_id))

#         print("Creating an API key")
#         r = sess.post(
#             os.path.join(home, "api_keys"),
#             json={"user_id": user["id"], "clone_id": clone_id},
#         )
#         print(r.json())
#         api_key = r.json()["key"]
#         api_key_json = r.json()
#         print("api_key:", api_key, "\n-----\n")

#         print("Checking we can get an API key")
#         r = sess.get(os.path.join(home, "api_keys"), params=dict(user_id=user["id"]))

#         sess.headers.update({"CLONR_API_KEY": api_key})

#         print("Creating a Conversation")
#         r = sess.post(
#             os.path.join(home, "conversations"),
#             json=dict(name="Makima-convo-1", clone_id=clone_id),
#         )
#         print(r.json())
#         convo_id = r.json()["id"]

#         print("Getting Conversations for this API Key")
#         r = sess.get(
#             os.path.join(home, "conversations"),
#         )

#         print("Writing some Messages")
#         for msg in ["Hey Makima!", "Whats uppp?"]:
#             r = sess.post(
#                 os.path.join(home, "conversations", convo_id, "messages"),
#                 json=dict(content=msg, sender_name="Bob"),
#             )

#         print("Getting recent Messages")
#         r = sess.get(
#             os.path.join(home, "conversations", convo_id, "messages"),
#         )
#         messages = r.json()
