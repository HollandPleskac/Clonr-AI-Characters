from fastapi.testclient import TestClient

from tests.types import LoginData

# Idk why this is causing a deadlock when it runs at the same time as test_clones...
# def test_users(client: TestClient, user_headers: dict[str, str], user_data: LoginData):
#     # get user info
#     r = client.get("/users/me", headers=user_headers)
#     data = r.json()
#     assert r.status_code == 200, r.json()
#     assert data["email"] == user_data.email, data
