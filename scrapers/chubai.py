import os
import asyncio
import time
import random
from typing import Final
from pathlib import Path
import requests
import itertools
import pandas as pd
import aiohttp
from fire import Fire
from tqdm import tqdm
import logging
from tenacity import retry, wait_exponential, before_sleep_log


logger: Final = logging.getLogger(__name__)
logging.basicConfig(level=logging.INFO)


def scrape_homepage() -> pd.DataFrame:
    # scrape all front page characters, and link back with foreign key homepage_id
    url = "https://api.chub.ai/search"
    params = dict(sort="default", venus="false", min_tokens=50, first=100000, page=1)
    all_characters_response = requests.get(url, params=params)
    all_characters = all_characters_response.json()["data"]["nodes"]
    df_chars = pd.DataFrame(all_characters)
    df_chars["homepage_id"] = list(range(len(df_chars)))

    return df_chars


@retry(
    wait=wait_exponential(),
    before_sleep=before_sleep_log(logger, logging.INFO),
)
async def _scrape_card(session, path, homepage_id):
    url = f"https://api.chub.ai/api/characters/{path}?full=true"
    async with session.get(url) as r:
        if r.status != 200:
            print("Error craping Character Card. path:", path)
            raise ValueError(r.status)
        data = await r.json()
        maybe_creator = path.split("/")[0]
        packet = {
            **data["node"],
            "maybe_creator": maybe_creator,
            "homepage_id": homepage_id,
        }
        return packet


async def scrape_character_cards(df_chars: pd.DataFrame, bsz: int = 16) -> pd.DataFrame:
    # make some coroutines
    character_cards = []
    with tqdm(total=len(df_chars)) as pbar:
        async with aiohttp.ClientSession() as session:
            coroutines = []
            for _, row in df_chars.iterrows():
                homepage_id = row.homepage_id
                path = row.fullPath
                coroutines.append(_scrape_card(session, path, homepage_id))
            for j in range(0, len(coroutines), bsz):
                cur = await asyncio.gather(*coroutines[j : j + bsz])
                character_cards.extend(cur)
                pbar.update(len(coroutines[j : j + bsz]))
                await asyncio.sleep(random.random() * 2)

    if not character_cards:
        raise ValueError()
    df_cards = pd.DataFrame(character_cards)
    df_cards["card_id"] = list(range(len(df_cards)))

    return df_cards


@retry(
    wait=wait_exponential(),
    before_sleep=before_sleep_log(logger, logging.INFO),
)
def scrape_lorebooks(df_chars):
    lorebooks = []
    row_errors = []

    lorebook_ids = list(
        filter(
            lambda x: x >= 0, itertools.chain.from_iterable(df_chars.related_lorebooks)
        )
    )

    for lorebook_id in tqdm(lorebook_ids):
        if lorebook_id < 0:
            continue
        url = "https://api.chub.ai/api/v4/projects/200945/repository/files/raw%252Fsillytavern_raw.json/raw"
        params = dict(ref="main", response_type="blob")
        r = requests.get(url, params=params)
        if r.status_code != 200:
            print("Error Scraping Lorebooks. Lorebook ID:", lorebook_id)
            raise ValueError(r.status)
        lorebooks.append(r.json())

    df_lorebooks = pd.DataFrame(lorebooks)

    return df_lorebooks


async def main(output_dir: str):
    st = time.time()
    os.makedirs(output_dir, exist_ok=True)
    print("\033[0mScraping Homepage\033[1m")
    homepage = scrape_homepage()
    homepage.to_json(Path(output_dir) / "chubai_homepage.json", indent=2)

    print("\033[0mScraping Character Cards\033[1m")
    characters = await scrape_character_cards(homepage)
    characters.to_json(Path(output_dir) / "chubai_characters.json", indent=2)

    print("\033[0mScraping Lorebooks\033[1m")
    lorebooks = scrape_lorebooks(homepage)
    lorebooks.to_json(Path(output_dir) / "chubai_lorebooks.json", indent=2)
    print("Total time:", round(time.time() - st, 2))


if __name__ == "__main__":
    Fire(main)
