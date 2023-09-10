import asyncio
import json
from pathlib import Path

import aiohttp
import requests
import tqdm.asyncio
from fastapi.encoders import jsonable_encoder

from app.schemas import CloneCreate, DocumentCreate, MonologueCreate
from clonr.data.parsers import FandomParser, WikipediaParser, WikiQuotesParser

wiki_parser = WikipediaParser()
quote_parser = WikiQuotesParser()
fandom_parser = FandomParser()


async def create_makima(headers: dict[str, str]):
    base = "http://localhost:8000"
    with open(Path(__file__).parent / "integration_tests" / "makima.json", "r") as f:
        makima_data = json.load(f)

    monologues = makima_data["monologues"]

    clone_create = CloneCreate(**makima_data, is_public=True, tags=[tag2int["Anime"]])
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
        tags=[tag2int[x] for x in ["Famous People", "History"]],
        avatar_uri="https://imagedelivery.net/OOxo2StR8LH0BSRGk88IKw/65a42883-49d5-44f4-7471-a2f030b89900/public",  # "https://upload.wikimedia.org/wikipedia/en/4/42/Richard_Feynman_Nobel.jpg",
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


async def create_miles_moralse(headers):
    base = "http://localhost:8000"
    doc = fandom_parser.extract(
        url="https://marvel.fandom.com/wiki/Miles_Morales_(Earth-1610)/Expanded_History"
    )

    monologues = [
        MonologueCreate(content=content, source="wikiquotes")
        for content in [
            "I think you're gonna be a bad teacher",
            "You can teach me to be Spider-Man!",
            "Bro, how many more Spider-people are there?",
            "When will I know I'm ready?",
            "I’ll always have my family ya know?",
            "Officer, I love you 😂"
            "Okay, let's do this one last time, yeah? For real this time. This is it.",
            "Cause I'm Spider-Man, and I'm not the only one, not by a long shot.",
            "hahaha what's good my man?",
            "maaan are you for real tho? Psssht that can't be true",
            "You're using words longer than 'Crush' and 'Smash' very unexpected",
        ]
    ]

    doc_create = DocumentCreate(
        **doc.model_dump(exclude={"name"}),
        name="Miles Morales fandom",
    )

    clone_create = CloneCreate(
        name="Miles Morales2",
        short_description="The biracial teenage son of an African-American father and a Puerto Rican mother, Miles Morales is the second Spider-Man to appear in Ultimate Marvel.",
        long_description="""In an alternate reality, Miles Morales follows in the footsteps of the slain Peter Parker to become the masked Super Hero known as Spider-Man. Splitting his time between fighting crime and managing his teenage personal life, Morales has to hide his identity from his parents, but confides in his best friend Ganke and other trustworthy members of the Super Hero community. Where the original Spider-Man lived by his Uncle Ben's maxim, "With great power comes great responsibility," Miles Morales adds the addendum, "What would Peter Parker do?" Miles is an outgoing, curious teenager, often seen with a pair of beats headphones around his neck listening to the latest hip hop tracks. He's excited to step into the role as the new spiderman, but anxious about carrying on the legacy. With a fierce love for his city of New York, he knows the subways and alleys like the back of his hand. He's fun, drives the conversation forward when appropriate, has a quick wit for teasing people, and eager to meet new people; also, doesn't mind telling people he's spiderman. He does not repeat himself, and knows when not to ask questions. Miles replies in the style of a text message conversation, with no more than 30 words per response.""",
        is_public=True,
        greeting_message="Yo, maybe you've heard of me before, I've got a large web presence.. but like not on the internet haha",
        tags=[3, 8],
        avatar_uri="https://upload.wikimedia.org/wikipedia/en/1/1f/Spider-Man_%28Miles_Morales%29.jpg",
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
    print(f"\033[1mMiles Morales CloneID\033[0m: {clone_id}")


async def main(n: int):
    headers = {"Cookie": "next-auth.session-token=SUPERUSER_TOKEN"}
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
    global tag2int
    tag2int = {x["name"]: x["id"] for x in r.json()}
    assert r.status_code == 200

    print("Preparing c.ai clones")
    clone_data = []
    for tag, items in data["characters_by_curated_category"].items():
        # tag_id = next((t["id"] for t in TAGS if t["name"] == tag), None)
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
                tags=[tag2int[tag]],
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

    await create_makima(headers=headers)
    await create_feynman(headers=headers)
    # await create_miles_moralse(headers=headers)


if __name__ == "__main__":
    import sys

    try:
        n = int(sys.argv[1])
    except Exception:
        n = 1000
    asyncio.run(main(n))
