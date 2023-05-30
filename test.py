import os

import requests
from dotenv import load_dotenv
from fastapi.encoders import jsonable_encoder
from sqlalchemy import select

load_dotenv()


home = "http://localhost:8000"
register_url = os.path.join(home, "auth/register")
jwt_url = os.path.join(home, "auth/jwt/login")


if __name__ == "__main__":
    with requests.session() as sess:
        r = sess.post(
            jwt_url,
            data=dict(
                username=os.environ["SUPERUSER_EMAIL"],
                password=os.environ["SUPERUSER_PASSWORD"],
            ),
        )
        auth_header = {"Authorization": "Bearer " + r.json()["access_token"]}
        sess.headers.update(auth_header)
        r = sess.get(os.path.join(home, "users/me"))
        r = sess.post(os.path.join(home, "clones"), json={})
        clone_id = r.json()["id"]
        # r = sess.patch(os.path.join(home, 'clones', clone_id), json={'is_public':True})
        r = sess.get(os.path.join(home, "clones", clone_id))
        r = sess.put(os.path.join(home, "clones", clone_id), json={"is_public": True})
        r = sess.delete(os.path.join(home, "clones", clone_id))
        r = sess.get(os.path.join(home, "clones", clone_id))
        assert r.status_code >= 400

        r = sess.post(os.path.join(home, "clones"), json={})
        clone_id = r.json()["id"]

        user_id = sess.get(os.path.join(home, "users", "me")).json()["id"]
        r = sess.post(
            os.path.join(home, "apikeys"),
            json={"clone_id": clone_id, "user_id": user_id},
        )
        api_key = r.json()["key"]
        print(r.json())

        r = sess.post(
            os.path.join(home, "apikeys"),
            json={"clone_id": clone_id, "user_id": user_id},
        )
        print(r.json())

        sess.headers.update({"CLONR_API_KEY": api_key})
        r = sess.post(os.path.join(home, "conversations"))
        convo_id = r.json()["id"]

        r = sess.get(os.path.join(home, "conversations", convo_id, "messages"))
        # r = sess.post(os.path.join(home, 'conversations', convo_id, 'messages'), json={'message':'Hey whats up??'})
