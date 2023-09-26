import re
from enum import Enum
import pandas as pd
from tqdm import tqdm

tqdm.pandas()
from fuzzywuzzy.fuzz import partial_ratio

import os

os.chdir("backend")
from app.utils import ratings_rank_score
from app.external.moderation import (
    openai_moderation_check,
    ModerationResult,
    openai_moderation_check_synchronous,
)
from clonr.tokenizer import Tokenizer

tokenizer = Tokenizer.from_openai("gpt-3.5-turbo")
os.chdir("..")


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
    if x := re.search(r"suicide|\braped?\b|\brapist\b|kill\s*\w+self|schizophren", s):
        return True


def misc_banned_words(s: str):
    if x := re.search(
        r"4chan|\bfurry\b|\bnazis?\b|\bincel\b|\bfemcel\b|jihad|\banthros?\b|hitler|magical\s*pony|drug\s*addict",
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


import json
import ast
from urllib.parse import unquote

df = pd.read_csv("~/Downloads/filtered-clones-beta - chub-needs-edits.csv")
df.final_links = df.final_links.fillna("[]").map(ast.literal_eval)
df.short_description = df.short_description.fillna("").map(
    lambda x: re.split(r"\s*\-\s*Token", x)[0]
)


# this works for wikipedia and fandom URLs, they use the name in the path
def link_similarity_score(row):
    res = 0
    links = row["final_links"]
    if (pd.isnull(row["drop"]) or not row["drop"]) and links:
        for link in links:
            link = unquote(link)
            link = re.sub(
                r"[^a-zA-Z0-9]", "", link.split("/")[-1].lower()
            )  # get path name
            for comp_str in [row["name"], row["long_description"]]:
                if comp_str:
                    comp_str = re.sub(r"[^a-zA-Z0-9]", "", comp_str.lower())
                    res = max(res, partial_ratio(comp_str, link))
    return res


manual_mask = df["drop"].fillna(False).map(bool)
print("Manual mask:", manual_mask.sum())

cai_mask = df.short_description.fillna("").str.contains(r"\bcai\b", case=False)
print("CAI mask:", cai_mask.sum())

flag_content_mask = df.fillna("").apply(
    lambda x: flag_content(
        " ".join(
            str(v)
            for k, v in x.items()
            if k
            in [
                "name",
                "short_description",
                "long_description",
                "greeting",
                "example_dialogues",
            ]
        )
    )
    != ContentFlag.ok,
    axis=1,
)
print("flag content mask:", flag_content_mask.sum())

null_field_mask = df.long_description.isna() | df.greeting.isna()
print("Null fields mask:", null_field_mask.sum())

lens = df.fillna("").apply(
    lambda x: tokenizer.length(x["long_description"] + x["example_dialogues"]), axis=1
)
too_short_mask = lens < 150
print("Too short mask:", too_short_mask.sum())

too_long_mask = lens >= 1600
print("Too long mask:", too_long_mask.sum())

bad_score_mask = (df.wilson_score > 0) & (df.wilson_score < 0.4)
print("Bad score mask:", bad_score_mask.sum())

scrs = df.fillna("").apply(link_similarity_score, axis=1)
bad_links_mask = (scrs <= 0.9) & df.final_links.map(bool)
print("Bad links mask:", bad_links_mask.sum())

mask = (
    manual_mask
    | cai_mask
    | flag_content_mask
    | null_field_mask
    | too_short_mask
    | too_long_mask
    | bad_score_mask
    | bad_links_mask
)
print("Total mask:", mask.sum())
