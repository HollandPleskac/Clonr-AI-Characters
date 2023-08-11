import asyncio
import json

import aiohttp
import requests
import tqdm.asyncio

from app.schemas import CloneCreate
from app.settings import settings


async def main():
    print("Getting Superuser credentials")
    r = requests.post(
        "http://localhost:8000/auth/cookies/login",
        data=dict(
            username=settings.SUPERUSER_EMAIL, password=settings.SUPERUSER_PASSWORD
        ),
    )

    headers = {"Cookie": r.headers["set-cookie"].split(";")[0]}
    r = requests.get("http://localhost:8000/users/me", headers=headers)

    print("Loading scraped c.ai data")
    with open("../clonr/data/scrapers/results.json", "r") as f:
        data = json.load(f)

    print("Creating default Tags")
    for k in data["characters_by_curated_category"]:
        r = requests.post(
            "http://localhost:8000/tags/", headers=headers, json=dict(name=k)
        )
        r.raise_for_status()
    r = requests.get(
        "http://localhost:8000/tags", headers=headers, params=dict(limit=2)
    )
    r.raise_for_status()
    assert r.status_code == 200

    print("Preparing c.ai clones")
    clone_data = []
    for tag, items in data["characters_by_curated_category"].items():
        for item in items:
            avatar_uri = f"https://characterai.io/i/400/static/avatars/{item['avatar_file_name']}"
            long_description = item["title"] + "\n" + item["greeting"]
            if len(long_description) < 32:
                continue
            if len(item["title"]) < 3:
                item["title"] = " ".join(long_description.split()[:3])
            x = CloneCreate(
                name=item["participant__name"],
                short_description=item["title"],
                greeting_message=item["greeting"],
                avatar_uri=avatar_uri,
                long_description=long_description,
                is_public=True,
                tags=[tag],
            )
            clone_data.append(x.model_dump())

    print("Uploading c.ai clones")
    async with aiohttp.TCPConnector(limit=64) as tcp_connection:
        async with aiohttp.ClientSession(connector=tcp_connection) as session:
            tasks = []
            for x in clone_data:
                task = session.post(
                    url="http://localhost:8000/clones", json=x, headers=headers
                )
                tasks.append(task)
            await tqdm.asyncio.tqdm_asyncio.gather(*tasks)


if __name__ == "__main__":
    asyncio.run(main())
