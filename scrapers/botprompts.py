import re
import requests
import json
import pandas as pd
import os
import time
from typing import Set
from datetime import datetime
from tqdm import tqdm
from fire import Fire
from bs4 import BeautifulSoup

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
    except:
        try:
            cur = [x.strip() for x in re.search(pattern2, x).groups()]
            entry = dict(
                zip(("char_name", "universe", "creator"), (cur[0], None, cur[-1]))
            )
            return entry
        except:
            return dict(zip(("char_name", "universe", "creator"), (x, None, None)))


def main(output: str):
    data: list[dict] = []
    vis_urls: Set[str] = set()
    error_urls: Set[str] = set()
    error_links: list[dict] = []

    st = time.time()

    for url in URLS:
        print("Extracting from:", url.split("/")[-1])

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

        # iterate in each category
        for link in tqdm(links):
            if link["url"] in vis_urls:
                continue
            try:
                r = requests.get(link["url"])
                payload = r.json()
                try:
                    if "metadata" in payload:
                        date = datetime.utcfromtimestamp(
                            payload["metadata"]["created"] / 1000
                        ).isoformat()
                        payload["created_at"] = date
                except Exception:
                    print("couldn't get datetime")
                char = {**link, **payload}
                data.append(char)
                vis_urls.add(char["url"])
            except Exception:
                error_urls.add(char["url"])
                error_links.append(link)

    df = pd.DataFrame(data)
    df.to_csv(output)
    print(f"Errored on: {error_links}")
    print(f"Scraped {len(data)} characters, with {len(error_links)} errors.")
    print(f"{time.time() - st:.02f}s to scrape {len(data)} bots.")


if __name__ == "__main__":
    Fire(main)
