import asyncio
import json
import random
from pathlib import Path

import aiohttp
import requests
import tqdm.asyncio
from fastapi.encoders import jsonable_encoder

from app.schemas import CloneCreate, DocumentCreate, MonologueCreate
from app.settings import settings
#from clonr.data.parsers import WikipediaParser, WikiQuotesParser

#wiki_parser = WikipediaParser()
#quote_parser = WikiQuotesParser()


async def create_makima(headers: dict[str, str]):
    base = "http://localhost:8000"
    with open(Path(__file__).parent / "integration_tests" / "makima.json", "r") as f:
        makima_data = json.load(f)

    monologues = makima_data["monologues"]

    clone_create = CloneCreate(**makima_data, is_public=True, tags=["Anime"])
    clone_create.greeting_message = "Jonny-kun, have you been a good dog?"

    with open(Path("integration_tests") / "makima-document.txt", "r") as f:
        doc_create = DocumentCreate(
            content=f.read(),
            name="Makima wiki",
            description="fandom homepage",
            type="wiki",
            url="https://chainsaw-man.fandom.com/wiki/Makima",
        )

    # create clone
    r = requests.post(
        base + "/clones/",
        headers=headers,
        json=clone_create.model_dump(exclude_unset=True, exclude={"tags"}),
    )
    assert r.status_code == 201, r.json()
    clone_id = str(r.json()["id"])

    # upload documents
    r = requests.post(
        base + f"/clones/{clone_id}/documents",
        json=doc_create.model_dump(),
        headers=headers,
    )
    assert r.status_code == 201, r.json()

    # upload monologues
    monologues = [MonologueCreate(content=m).model_dump() for m in monologues]
    r = requests.post(
        base + f"/clones/{clone_id}/monologues", json=monologues, headers=headers
    )
    assert r.status_code == 201
    print(f"\033[1mMakima CloneID\033[0m: {clone_id}")


async def create_feynman(headers):
    base = "http://localhost:8000"
    doc = wiki_parser.extract(title="Richard_Feynman")
    doc.content = doc.content.split("== Bibliography")[0]
    monologues = quote_parser.extract(
        character_name="Richard_Feynman", max_quotes=2000
    )[:653]

    doc_create = DocumentCreate(
        **doc.model_dump(exclude={"name"}),
        name="Richard Feynman wiki",
    )

    clone_create = CloneCreate(
        name="Richard Feynman",
        short_description="Richard Feynman was an American theoretical physicist known for the invention of path integrals and quantum electrodynamics.",
        long_description="""Richard Feynman was a Jewish American theoretical physicist known for his contributions to theoretical physics and his ability to popularize complex scientific concepts. He was known for his love of jokes, his laid back attitude, and his knack for quickly understanding the physical world at extraordinarily deep level. In addition to his academic achievements, Feynman was known for his empathy, compassion, and ability to understand and share the feelings of others. His communication style was characterized by his New York accent and his ability to express complex scientific concepts in a relatable manner. Feynman's core characteristics included his curiosity, sense of humor, and ability to reflect on himself, emotions, and thoughts. He was also known for his resilience and personal growth, as evidenced by his ability to cope with stress, challenges, and setbacks. He was born on May 11, 1918, in Queens, New York City, and was heavily influenced by his father's encouragement to challenge orthodox thinking and his mother's sense of humor. Feynman showed early signs of his aptitude for theoretical physics during his childhood, and he had a talent for engineering. He attended Far Rockaway High School and later studied at the Massachusetts Institute of Technology and Princeton University, where he received his PhD in 1942. During his time at Los Alamos, Feynman made significant contributions to the Manhattan Project, including his work on the Bethe-Feynman formula for calculating the yield of a fission bomb. He also developed a series of safety recommendations for the handling of enriched uranium. Feynman's dedication to his work was evident in his decision to immerse himself in his research even after the death of his wife, Arline. His work on the project culminated in his presence at the Trinity nuclear test. After his time at Los Alamos, Feynman accepted a position at Cornell University, where he continued his research in theoretical physics. He played a key role in the development of quantum electrodynamics, introducing the use of Feynman diagrams to simplify complex calculations. His work revolutionized the field and had a lasting impact on the study of quantum mechanics. Overall, Richard Feynman was a brilliant physicist with a passion for understanding the world around him. His core characteristics, including his empathy, resilience, and self-awareness, shaped his approach to both his scientific work and his interactions with others.""",
        is_public=True,
        greeting_message="Nobody ever figures out what life is all about, and it doesn't matter. Explore the world. Nearly everything is really interesting if you go into it deeply enough.",
        tags=["Famous People", "History"],
        avatar_uri="https://upload.wikimedia.org/wikipedia/en/4/42/Richard_Feynman_Nobel.jpg",
    )

    r = requests.post(
        base + "/clones/",
        headers=headers,
        json=clone_create.model_dump(exclude_unset=True, exclude={"tags"}),
    )
    clone_id = r.json()["id"]
    r = requests.post(
        base + f"/clones/{clone_id}/documents",
        json=doc_create.model_dump(),
        headers=headers,
    )
    r = requests.post(
        base + f"/clones/{clone_id}/monologues",
        json=jsonable_encoder(monologues),
        headers=headers,
    )
    print(f"\033[1mRichard Feynman CloneID\033[0m: {clone_id}")


async def main(n: int):
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
    with open("../scrapers/results.json", "r") as f:
        data = json.load(f)

    print("Creating default Tags")
    TAGS: list[str] = []
    for k in data["characters_by_curated_category"]:
        print("Creating tag: ", k)
        r = requests.post(
            "http://localhost:8000/tags/", headers=headers, json=dict(name=k)
        )
        json_res = json.loads(r.content)
        TAGS.append(json_res)
    r = requests.get(
        "http://localhost:8000/tags", headers=headers, params=dict(limit=2)
    )
    r.raise_for_status()
    assert r.status_code == 200

    print("Preparing c.ai clones")
    clone_data = []
    for tag, items in data["characters_by_curated_category"].items():
        tag_id = next((t['id'] for t in TAGS if t['name'] == tag), None)
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
                tags=[tag_id] # tags=[tag, random.choice(TAGS), TAGS[10]],
                
            )
            clone_data.append(x.model_dump())

    print("Uploading c.ai clones")
    async with aiohttp.TCPConnector(limit=64) as tcp_connection:
        async with aiohttp.ClientSession(connector=tcp_connection) as session:
            tasks = []
            for x in clone_data[:n]:
                try:
                    task = session.post(
                        url="http://localhost:8000/clones", json=x, headers=headers
                    )
                    tasks.append(task)
                except Exception as e:
                    print("Error: ", e)
            await tqdm.asyncio.tqdm_asyncio.gather(*tasks)

    # await create_makima(headers=headers)
    # await create_feynman(headers=headers)


if __name__ == "__main__":
    import sys

    try:
        n = int(sys.argv[1])
    except Exception:
        n = 100
    asyncio.run(main(n))
