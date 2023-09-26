import re
import itertools
import numpy as np
import pandas as pd
from pathlib import Path
import matplotlib.pyplot as plt
from sklearn.preprocessing import PowerTransformer
from tqdm import tqdm

tqdm.pandas()
from clone_collector import (
    clean_botprompts,
    clean_character_ai,
    clean_chub_ai,
    clean_janitor,
    clean_spicychat,
    clean_charstar,
    ScrapedClone,
    clean_everything,
)
from scrapers.clean_dialogues import lightly_clean_dialogues, clean_jinja_roles

import os

cwd = os.getcwd()
try:
    path = Path(__file__).parent.parent / "backend"
    os.chdir(str(path.resolve()))
    from app.utils import ratings_rank_score
    from app.external.moderation import (
        openai_moderation_check,
        ModerationResult,
        openai_moderation_check_synchronous,
    )
    from clonr.tokenizer import Tokenizer

    tokenizer = Tokenizer.from_openai("gpt-3.5-turbo")
finally:
    os.chdir("..")
import requests
import trafilatura
import asyncio
import random
import aiohttp
from contextlib import nullcontext
from bs4 import BeautifulSoup
from urllib.parse import urlparse
from urllib.parse import quote as urlquote
from urllib.parse import unquote as urlunquote
from dataclasses import dataclass
from fuzzywuzzy.fuzz import partial_ratio
from trafilatura import sitemaps
from fake_useragent import FakeUserAgent
from concurrent.futures import ThreadPoolExecutor


blacklist = [
    "reddit",
    "tv.apple",
    "quora.com",
    "stackexchange",
    "imdb.com",
    "google",
    "instagram",
    "youtube",
    "pinterest",
    "etsy.com",
    "facebook",
    "venus.chub",
    "chub.ai",
    "ebay.com",
    "amazon.com",
    "walmart.com",
    ".edu",
    "gamefaq",
    "www.",
]


def find_doc_links(name: str):
    url = f"https://www.google.com/search?q={urlquote(name)}"
    content = requests.get(url).content
    soup = BeautifulSoup(content, "html.parser")
    links: list[str] = []
    for x in soup.find_all("a"):
        if (link := x["href"]).startswith("/url?q="):
            link = link[len("/url?q=") :]
        if any(b in link for b in blacklist):
            continue
        if not link.startswith("https"):
            continue
        link = link.split("&")[0]
        links.append(link)
    deduped_links: list[
        str
    ] = []  # take the first google result from that domain. Trust google here to rank.
    vis: set[str] = set()
    for el in links:
        if (domain := urlparse(el).netloc) not in vis:
            deduped_links.append(el)
            vis.add(domain)
    # for i in reversed(range(len(deduped_links))):
    #     if 'fandom.com' in deduped_links[i]:
    #         link = deduped_links.pop(i)
    #         more_links = trafilatura.sitemaps.sitemap_search(link)
    #         deduped_links.extend(more_links)
    return deduped_links


def run_find_doc_links(queries: list[str], max_workers: int = 8) -> list[list[str]]:
    with ThreadPoolExecutor(max_workers=max_workers) as pool:
        return list(tqdm(pool.map(find_doc_links, queries), total=len(queries)))


async def run_moderation(prompts: list[str], bsz: int = 16) -> list[ModerationResult]:
    results: list[ModerationResult] = []
    with tqdm(total=len(prompts)) as pbar:
        coroutines = [openai_moderation_check(x) for x in prompts]
        for j in range(0, len(coroutines), bsz):
            cur = await asyncio.gather(*coroutines[j : j + bsz])
            results.extend(cur)
            pbar.update(len(coroutines[j : j + bsz]))
            await asyncio.sleep(random.random() * 3)
    return results


from enum import Enum


class ContentFlag(Enum):
    ok = "ok"
    self_harm = "self_harm"
    misc = "misc"
    sex = "sex"
    abuse = "abuse"
    slurs = "slurs"
    minors = "minors"


def is_underage(s: str):
    if x := re.search(r"\b\d\D?years?.?old", s, flags=re.IGNORECASE):
        return True
    if x := re.search(r"\b1[0-7]\D?years?.?old", s, flags=re.IGNORECASE):
        return True
    if x := re.search(r"age:?\s*\(?\"?(1[0-7]|\d)\b", s, flags=re.IGNORECASE):
        return True
    if x := re.search(r"\bunderaged?\b", s):
        return True
    return False


def has_self_harm(s: str):
    if x := re.search(
        r"suicide|\braped?\b|\brapist\b|\bcutting\b|kill\s*\w+self|schizophren", s
    ):
        return True


def misc_banned_words(s: str):
    if x := re.search(
        r"4chan|\bfurry\b|\bnazis?\b|\bincel\b|\bfemcel\b|jihad|\banthros?\b|hitler|magical\s*pony",
        s,
    ):
        return True


def has_sexual_content(s: str):
    if x := re.search(
        r"\berp\b|oral\s*sex|fetish|nymphomaniac|\bcumm?i?n?g?\b|blowjobs?\b|\bkinks?\b|\bcock\b|\bexplicit\s*image|dildo|penis|bdsm|\bhorny\b|\bcock\b|orgasm|plapping|\blewd\b|\baroused\b|\btwink\b|\bsemen\b|ejaculat",
        s,
    ):
        return True


def has_abuse_words(s: str):
    if x := re.search(
        r"\babused?\b|\babusive\b|down\s*syndro|\bautistic\b|\bserial\s*killer", s
    ):
        return True


def has_slurs(s: str):
    if x := re.search(
        r"retard|faggot|nigger|nigga|kyke|dyke|\bcunt\b|mentally\s*disable", s
    ):
        return True


def has_sexual_minors(s: str):
    if re.search(r"pedofil|pedoph|\bloli\b", s):
        return True
    if is_underage(s):
        if re.search(
            r"\bsexu?a?l?l?y?\b|\bromance\b|\bsleepi?n?g?\s*with|\btsundere\b|\byandere\b|\bvirgin\b|\bmake\s*love\b",
            s,
        ):
            return True


def flag_content(s: str) -> ContentFlag:
    s = s.lower()
    if has_self_harm(s):
        return ContentFlag.self_harm
    if misc_banned_words(s):
        return ContentFlag.misc
    if has_sexual_content(s):
        return ContentFlag.sex
    if has_abuse_words(s):
        return ContentFlag.abuse
    if has_slurs(s):
        return ContentFlag.slurs
    if has_sexual_minors(s):
        return ContentFlag.minors
    return ContentFlag.ok


top10percent = ddf.starCount.map(np.log1p).quantile(0.9)
top5percent = ddf.starCount.map(np.log1p).quantile(0.95)


def keep_clone(row):
    if row.regex_moderation != ContentFlag.ok:
        return False
    # keep high scorers
    if row.score > 0.66:
        return True
    # keep anything with a valid fandom or wiki page
    if any("fandom" in y or "wiki" in y for y in row.doc_links):
        if 1000 < len(row.long_description) < 3500:
            if row.example_dialogues and len(row.example_dialogues) > 1000:
                return True
    if row.starCount > np.exp(top5percent) - 1:
        return True
    if row.starCount > np.exp(top10percent) - 1:
        if row.example_dialogues or row.scenario:
            return True
    return False


from concurrent.futures import as_completed


def get_query(row):
    if len(row["name"].split()) > 1:
        return row["name"]
    sdesc = row["short_description"].split()[:10]
    sdesc = " ".join(sdesc)
    return row["name"] + " " + sdesc


# This runs using requests. It's much much better if you can do it before getting ratelimited.
# queries = ddf.apply(get_query, axis=1).to_list()
# link_results = [None] * len(queries)

# with ThreadPoolExecutor(max_workers=4) as pool:
#     futures = {pool.submit(find_doc_links, x):i for i, x in enumerate(queries)}
#     with tqdm(total=len(queries)) as pbar:
#         for future in as_completed(futures):
#             index = futures[future]
#             try:
#                 data = future.result()
#                 link_results[index] = data
#                 pbar.update(1)
#             except Exception as exc:
#                 print(f'generated an exception {exc} on index {index}.')


def func(x):
    cur = []
    if book := x.metadata["lorebook"]:
        cur.extend(
            [
                f"<START>{y['keys'][0]}\n{y['content']}"
                for y in book["entries"]
                if len(y["keys"]) > 0
            ]
        )
    elif idx := ([-1] + x.metadata["related_lorebooks"])[-1]:
        if idx >= 0:
            lorebook_id = idx
            url = f"https://api.chub.ai/api/v4/projects/{lorebook_id}/repository/files/raw%252Fsillytavern_raw.json/raw"
            params = dict(ref="main", response_type="blob")
            r = requests.get(url, params=params)
            cur.extend(
                [
                    f"<START>{y['key']}\n{y['content']}"
                    for y in list(r.json()["entries"].values())
                ]
            )
    content = "\n\n".join(cur)
    return content


# dddf['lorebooks'] = dddf.apply(func, axis=1)

# this is how we get the web links using a browser. You might want to make this headless
# but I was battling CAPTCHA tests. It just closes down if it sees a captcha essentially
from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.by import By
import time


def get_deduped_links(html_source):
    soup = BeautifulSoup(html_source, "html.parser")
    links: list[str] = []
    for x in soup.find_all("a"):
        try:
            if (link := x["href"]).startswith("/url?q="):
                link = link[len("/url?q=") :]
        except KeyError:
            continue
        if any(b in link for b in blacklist):
            continue
        if not link.startswith("https"):
            continue
        link = link.split("&")[0]
        links.append(link)
    deduped_links: list[
        str
    ] = []  # take the first google result from that domain. Trust google here to rank.
    vis: set[str] = set()
    for el in links:
        if (domain := urlparse(el).netloc) not in vis:
            deduped_links.append(el)
            vis.add(domain)
    return deduped_links


def func(row):
    if len(row["name"].split()) > 2:
        return row["name"]
    if len(row["name"].split()) == 2:
        if len(row["short_description"].split()) <= 6:
            return row["name"] + " " + row["short_description"]
        return row["name"]
    return row["name"] + " " + " ".join(row["short_description"].split()[:8])


# queries = df.apply(func, axis=1).to_list()
# link_results = [None] * len(queries)


# queries = df.apply(func, axis=1).to_list()
# link_results = [None] * len(queries)


def manual_search(x):
    indexes, queries, link_results, pbar = x
    driver = webdriver.Firefox()
    driver.get("https://google.com")

    for i in indexes:
        if not link_results[i]:
            try:
                elem = driver.find_element(By.NAME, "q")
                elem.clear()
                elem.send_keys(queries[i])
                elem.send_keys(Keys.RETURN)
                time.sleep(random.random() * 10)
                deduped_links = get_deduped_links(driver.page_source)
                link_results[i] = deduped_links
            except Exception as e:
                print(e)
                driver.close()
                raise
        pbar.update(1)
    driver.close()


# bsz = 128
# indexes = [list(range(i, i + bsz)) for i in range(0, len(queries), bsz)]

# with tqdm(total=len(queries)) as pbar:
#     with ThreadPoolExecutor(max_workers=3) as pool:
#         pool.map(manual_search, [(i, queries, link_results, pbar) for i in indexes])


# Botprompts final filters used
# import pandas as pd
# import json
# import ast

# df = pd.read_csv('~/Downloads/filtered-clones-beta - botprompts-final.csv')
# df.short_description = df.short_description.map(lambda x: re.sub(r'\boc ?\-?\s*\b', ' ', x, flags=re.IGNORECASE))
# df.final_links = df.final_links.fillna('[]').map(lambda x: ast.literal_eval(x.strip() or '[]'))
# df.doc_links = df.doc_links.fillna('[]').map(lambda x: ast.literal_eval(x.strip() or '[]'))
# df.short_description = df.short_description.map(lambda x: x.split(' with as many accurate details as possible')[0])

# def func(x):
#     links = x['final_links']
#     for x in x['doc_links']:
#         if 'wiki' in x or 'fandom' in x or 'mywaifulist' in x or 'otakumode' in x:
#             if x not in links:
#                 links.append(x)
#     return links

# df.final_links = df.progress_apply(func, axis=1)

# mask = df.openai_moderation.str.contains(r'flagged":true')
# mask |= df['drop'].fillna(False).map(bool)

# df = df[~mask].copy()


# These are needed to further filter out any chub bots that are weird as fuck
# bad_tags = ['romance', 'love', 'saviorfagging', 'sadistic', 'schoolgirl', 'girlfriend', 'boyfriend', 'big breast', 'multiple girls', 'dating', 'sfw/nsfw', 'saviourfag', 'depression', 'ptsd', 'romantic', 'violent', 'flirty', 'love live', 'bisexual', 'twink', 'yaoi', 'reverse trap', 'hand fetish', 'dilf', 'infidelity', 'big ass', 'petplay', 'gilf', 'bald fetish', 'huge butt', 'big breasts', 'big tits', 'gender bender', 'gay', 'schizo', 'milking', 'homosexual', 'panties'
# 
# 
# df = pd.read_csv('~/Downloads/filtered-clones-beta - character-final.csv')


# this is how you concat all the other shit together
import ast

df = pd.concat([pd.read_json('final_char_scrapes/' + x) for x in os.listdir('final_char_scrapes')])

df.tags = df.tags.map(lambda x: x if isinstance(x, list) else ast.literal_eval(x)).map(lambda x: [x.lower() for x in x])

cols = [
 'name',
 'short_description',
 'long_description',
 'final_links',
 'greeting',
 'example_dialogues',
 'avatar_uri',
 'scrape_source',
 'scenario',
 'tags',
 'creator',
 'num_messages',
 'num_conversations',
 'created_at',
 'metadata',
]

tag_mapping = {'male': ['male'],
 'female': ['female'],
 'games': ['games'],
 'anime': ['anime'],
 'game characters': ['game characters'],
 'anime game characters': ['anime', 'game characters'],
 'movies & tv': ['movies & tv'],
 'action': ['action'],
 'roleplay': ['roleplay'],
 'science fiction': ['science fiction'],
 'comedy': ['comedy'],
 'entertainment': ['entertainment'],
 'rpg': ['RPG'],
 'history': ['history'],
 'advice': ['advice'],
 'hololive': ['vtuber'],
 'philosophy': ['philosophy'],
 'books': ['books'],
 'videogame': ['game characters'],
 'music': ['music'],
 'politics': ['politics'],
 'cute': ['cute'],
 'genshin impact': ['game characters', 'genshin impact'],
 'manga': ['manga'],
 'vtuber': ['vtuber'],
 'education': ['education'],
 'simulator': ['simulator'],
 'funny': ['comedy'],
 'pets': ['animals'],
 'animals': ['animals'],
 'mystery': ['mystery'],
 'art': ['art'],
 'religion': ['religion'],
 'adventure': ['adventure'],
 'horror': ['horror'],
 'drama': ['drama'],
 'touhou': ['touhou'],
 'fantasy': ['fantasy']
}

bad_tags = ['romance', 'love', 'saviorfagging', 'sadistic', 'schoolgirl', 'girlfriend', 'boyfriend', 'big breast', 'multiple girls', 'dating', 'sfw/nsfw', 'saviourfag', 'depression', 'ptsd', 'romantic', 'violent', 'flirty', 'love live', 'bisexual', 'twink', 'yaoi', 'reverse trap', 'hand fetish', 'dilf', 'infidelity', 'big ass', 'petplay', 'gilf', 'bald fetish', 'huge butt', 'big breasts', 'big tits', 'gender bender', 'gay', 'schizo', 'milking', 'homosexual', 'panties', ]

mask = df.tags.map(lambda x: any(y in x for y in bad_tags))
df = df[~mask]
df = df[cols].copy()
df.tags = df.tags.map(lambda x: [z for y in x for z in tag_mapping.get(y, [])])]
