import os

import requests
from dotenv import load_dotenv

# from fastapi.encoders import jsonable_encoder
from sqlalchemy import select

load_dotenv()


home = "http://localhost:8000"
register_url = os.path.join(home, "auth/register")
jwt_url = os.path.join(home, "auth/jwt/login")


if __name__ == "__main__":
    with requests.session() as sess:
        print("Grabbing JWT")
        r = sess.post(
            jwt_url,
            data=dict(
                username=os.environ["SUPERUSER_EMAIL"],
                password=os.environ["SUPERUSER_PASSWORD"],
            ),
        )
        auth_header = {"Authorization": "Bearer " + r.json()["access_token"]}
        sess.headers.update(auth_header)

        print("Getting my own credentials")
        r = sess.get(os.path.join(home, "users/me"))
        user = r.json()
        print("user_id:", user["id"], "\n-----\n")

        print("Creating a Clone")
        r = sess.post(
            os.path.join(home, "clones"),
            json={
                "greeting_message": "Hi!",
                "name": "Makima",
                "description": "test",
                "motivation": "test",
            },
        )
        print(r.json())
        clone_id = r.json()["id"]
        print("clone_id:", clone_id, "\n-----\n")
        r = sess.get(os.path.join(home, "clones", clone_id))

        print("Creating an API key")
        r = sess.post(
            os.path.join(home, "api_keys"),
            json={"user_id": user["id"], "clone_id": clone_id},
        )
        print(r.json())
        api_key = r.json()["key"]
        api_key_json = r.json()
        print("api_key:", api_key, "\n-----\n")

        print("Checking we can get an API key")
        r = sess.get(os.path.join(home, "api_keys"), params=dict(user_id=user["id"]))

        sess.headers.update({"CLONR_API_KEY": api_key})

        print("Creating a Conversation")
        r = sess.post(
            os.path.join(home, "conversations"),
            json=dict(name="Makima-convo-1", clone_id=clone_id),
        )
        print(r.json())
        convo_id = r.json()["id"]

        print("Getting Conversations for this API Key")
        r = sess.get(
            os.path.join(home, "conversations"),
        )

        print("Writing some Messages")
        for msg in ["Hey Makima!", "Whats uppp?"]:
            r = sess.post(
                os.path.join(home, "conversations", convo_id, "messages"),
                json=dict(content=msg, sender_name="Jonny"),
            )

        print("Getting recent Messages")
        r = sess.get(
            os.path.join(home, "conversations", convo_id, "messages"),
        )
        messages = r.json()
