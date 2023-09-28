import re
import json
from collections import Counter


def lightly_clean_dialogues(s: str) -> str:
    """To be used with scraped dialogues for cleaning. Not really meant to be
    used in production"""
    # some weird colon shit. mostly happens with charstar
    s = re.sub(r"\s+:\s+", ": ", s)

    # Replace You: with {{user}}:
    s = re.sub(r"(^|\n)You:\s*", r"\1{{user}}: ", s, flags=re.IGNORECASE)
    s = re.sub(r"(^|\n)tuú?:\s*", r"\1{{user}}: ", s, flags=re.IGNORECASE)

    # replace missing user and char tags with colon
    s = re.sub(r"(^|\n)\{\{user\}\}\s+", r"\1{{user}}: ", s)
    s = re.sub(r"(^|\n)\{\{char\}\}\s+", r"\1{{char}}: ", s)

    # remove case sensitivity
    s = re.sub(r"\{\{(user)\}\}", r"{{user}}", s, flags=re.IGNORECASE)
    s = re.sub(r"\{\{(char)\}\}", r"{{char}}", s, flags=re.IGNORECASE)

    # replace missing braces user and char tags with
    s = re.sub(r"(?:^|\n)\{user\}\}?\s+", "\n{{user}}: ", s, flags=re.IGNORECASE)
    s = re.sub(r"(?:^|\n)\{char\}\}?\s+", "\n{{char}}: ", s, flags=re.IGNORECASE)

    # replace some weird non-brace role tokens
    pattern = r"(<user>)|(<<user>>)|(<you>)|(<<you>>)|\{you\}|(\{\{you\}\})|(\[user\])"
    s = re.sub(pattern, r"{{user}}", s, flags=re.IGNORECASE)
    pattern = r"(\{\{chara?c?t?e?r?\}\})|(\{chara?c?t?e?r?\}:?)|(<char>)|(<<char>>)|(<bot>)|(<<bot>>)|(\[chara?c?t?e?r?\])"
    s = re.sub(pattern, r"{{char}}", s, flags=re.IGNORECASE)

    # dialogues delimiter stuff. just use <START> as the common pattern
    pattern = r"(<end_of_dialogu?e?>)|(<<start>>)|(<start>)|(<<end>>)|(<end>)|(_?end_of_dialogu?e?_?)|(\[start\])|(\[dialogu?e?_? ?history\])"
    s = re.sub(pattern, "<START>", s, flags=re.IGNORECASE)

    lines = s.split("<START>")
    lines = [
        x.strip() for i, x in enumerate(lines) if x or (not x and not i)
    ]  # edge case if first chars are <START>
    s = "<START>\n".join(lines)

    return s


def clean_jinja_roles(s: str) -> str:
    # remove case sensitivity
    s = re.sub(r"\{\{(user)\}\}", r"{{user}}", s, flags=re.IGNORECASE)
    s = re.sub(r"\{\{(char)\}\}", r"{{char}}", s, flags=re.IGNORECASE)

    # replace missing braces user and char tags with
    s = re.sub(r"(?:^|\n)\{user\}\}?\s+", "\n{{user}} ", s, flags=re.IGNORECASE)
    s = re.sub(r"(?:^|\n)\{char\}\}?\s+", "\n{{char}} ", s, flags=re.IGNORECASE)

    # replace some weird non-brace role tokens
    pattern = r"(<user>)|(<<user>>)|(<you>)|(<<you>>)|\{you\}|(\{\{you\}\})|(\[user\])"
    s = re.sub(pattern, r"{{user}}", s, flags=re.IGNORECASE)
    pattern = r"(\{\{chara?c?t?e?r?\}\})|(\{chara?c?t?e?r?\}:?)|(<char>)|(<<char>>)|(<bot>)|(<<bot>>)|(\[chara?c?t?e?r?\])"
    s = re.sub(pattern, r"{{char}}", s, flags=re.IGNORECASE)

    return s


def get_dialogue_split_regex(s: str) -> str:
    split_regex_arr = [r"^{{char}}", r"\n{{char}}", r"^{{user}}", r"\n{{user}}"]
    if s:
        c = Counter([x.strip().split()[0] for x in s.split("\n") if x.strip()])
        N = sum(c.values())
        for k, v in c.items():
            if v > (N // 4):
                split_regex_arr.extend([f"^{k}", f"\n{k}"])
    split_regex = "(" + "|".join(split_regex_arr) + ")"
    return split_regex


def trim_dialogues(s: str, cutoff: int = 3500):
    if len(s) < cutoff:
        return s
    # attempt 1. Use <START> tokens
    cur = cutoff
    used_dialogues: list[str] = []
    dialogues = s.split("<START>")
    for d in dialogues:
        if len(d) > cur:
            break
        if d:
            used_dialogues.append(d)
            cur -= len(d)
    if cur < cutoff // 2:
        return "<START>".join(used_dialogues)

    # attempt 2. Split into lines

    # Determine the lines in case they don't use char. Split on anything that is
    # more common than 25%
    cur = cutoff
    used_lines: list[str] = []
    split_regex = get_split_regex(s)
    arr = re.split(split_regex, s)
    lines = ["".join(arr[i : i + 2]).strip() for i in range(1, len(arr) - 1, 2)]
    for x in lines:
        if len(x) > cur:
            break
        if x:
            used_lines.append(x)
            cur -= len(x)
    if cur < cutoff // 2:
        return "\n".join(used_lines)

    # attempt 3. It's the messed up giovanni one.
    try:
        lines = json.loads(s)["chat"]
    except Exception:
        return s[:3000]

    cur = cutoff
    used_lines: list[str] = []
    for x in lines:
        if len(x) > cur:
            break
        if x:
            used_lines.append(x)
            cur -= len(x)
    if cur < cutoff // 2:
        return "\n".join(used_lines)

    return s[:cutoff]


def trim_long_desc(s: str, cutoff: int = 3500):
    # attempt 1 split on newlines. pretty simple.
    if len(s) < cutoff:
        return s
    cur = cutoff
    used_lines: list[str] = []
    lines = s.split("\n")
    for d in lines:
        if len(d) > cur:
            break
        if d:
            used_lines.append(d)
            cur -= len(d)
    if cur < cutoff // 2:
        return "\n".join(used_lines)

    # attempt 2 split on latin-character sentences.
    lines = SentenceSplitterChars()._text_to_sentences(s)
    cur = cutoff
    for d in lines:
        if len(d) > cur:
            break
        if d:
            used_lines.append(d)
            cur -= len(d)
    if cur < cutoff // 2:
        return "\n".join(used_lines)

    return s[:cutoff]
