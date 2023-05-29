import os

import requests
from dotenv import load_dotenv
from fastapi.encoders import jsonable_encoder
from sqlalchemy import select

load_dotenv()


home = "http://localhost:8000"
register_url = os.path.join(home, "auth/register")
jwt_url = os.path.join(home, "auth/jwt/login")

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
