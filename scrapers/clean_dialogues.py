import re


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
