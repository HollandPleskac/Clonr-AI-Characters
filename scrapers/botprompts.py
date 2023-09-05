import re
import requests
import asyncio
import aiohttp
import pandas as pd
import time
from typing import Set
from datetime import datetime
from tqdm import tqdm
from fire import Fire
from bs4 import BeautifulSoup
import logging
from typing import Final
from tenacity import retry, wait_exponential, before_sleep_log, retry_if_exception_type

logger: Final = logging.getLogger(__name__)
logging.basicConfig(level=logging.INFO)


class RateLimitError(Exception):
    pass


# Manually picked these up, there weren't many and this was easier
# for some reason the ones at the root have "recent" and aren't assigned a category
# this be some wordpress bullshit
URLS = [
    "https://botprompts.net/",
    "https://botprompts.net/botprompts.net/anime",
    "https://botprompts.net/danganronpa",
    "https://botprompts.net/creators",
    "https://botprompts.net/botprompts.net/genshin",
    "https://botprompts.net/hololive",
    "https://botprompts.net/botprompts.net/irl",
    "https://botprompts.net/botprompts.net/oc",
    "https://botprompts.net/botprompts.net/pokemon",
    "https://botprompts.net/touhou",
    "https://botprompts.net/games",
    "https://botprompts.net/botprompts.net/other",
    "https://botprompts.net/botprompts.net/nsfw",
]


def process_link(x: str) -> dict:
    """Extracts the name, fictional universe the char belongs to, and creator name... kind of."""
    pattern = "(.+)\s*\((.+)\)\s*–\s*(.+)"
    pattern2 = r"(.+)\s*-\s*(.+)"

    try:
        cur = [x.strip() for x in re.search(pattern, x).groups()]
        entry = dict(zip(("char_name", "universe", "creator"), cur))
        return entry
    except Exception:
        try:
            cur = [x.strip() for x in re.search(pattern2, x).groups()]
            entry = dict(
                zip(("char_name", "universe", "creator"), (cur[0], None, cur[-1]))
            )
            return entry
        except Exception:
            return dict(zip(("char_name", "universe", "creator"), (x, None, None)))


@retry(
    wait=wait_exponential(),
    before_sleep=before_sleep_log(logger, logging.INFO),
    retry=retry_if_exception_type(RateLimitError),
)
async def scrape_link(link: dict, session):
    try:
        async with session.get(link["url"]) as r:
            if r.status != 200:
                print(r.status)
                raise RateLimitError
            payload = await r.json()
        try:
            if "metadata" in payload:
                date = datetime.utcfromtimestamp(
                    payload["metadata"]["created"] / 1000
                ).isoformat()
                payload["created_at"] = date
        except Exception:
            print("couldn't get datetime")
        char = {**link, **payload}
        return char
    except Exception:
        print("ERROR:", link)


async def main(output: str):
    data: list[dict] = []
    st = time.time()
    all_links = []
    print("Gathering all data URLs")
    for url in tqdm(URLS):
        # Grabs the url link to a json file, and uses that link to figure out the name/universe/creator
        r = requests.get(url)
        soup = BeautifulSoup(r.content, "html.parser")
        links = [
            {"url": x["href"], "name": x.text, "tag": url.split("/")[-1]}
            for x in soup.find_all("a")
        ]
        links = [x for x in links if x["url"].endswith("json")]
        links = [
            {"url": x["url"], "tag": x["tag"], **process_link(x["name"])} for x in links
        ]
        all_links.extend(links)

    bsz = 16
    print("Scraping!")
    async with aiohttp.ClientSession() as session:
        with tqdm(total=len(all_links)) as pbar:
            for i in range(0, len(all_links), bsz):
                cur = await asyncio.gather(
                    *[scrape_link(x, session) for x in all_links[i : i + bsz]]
                )
                cur = [x for x in cur if x is not None]
                data.extend(cur)
                pbar.update(len(all_links[i : i + bsz]))

    df = pd.DataFrame(data)
    df.to_json(output)
    print(f"Scraped {len(data)} characters.")
    print(f"{time.time() - st:.02f}s to scrape {len(data)} bots.")


if __name__ == "__main__":
    Fire(main)
