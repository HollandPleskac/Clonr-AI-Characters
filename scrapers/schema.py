import pandas as pd
from tqdm import tqdm

tqdm.pandas()
import os

os.chdir("backend")
from pydantic import BaseModel
from clonr.text_splitters import aggregate_with_overlaps
from clonr.tokenizer import Tokenizer
from typing import Any
from datetime import datetime
import re

os.chdir("../")

tokenizer = Tokenizer.from_openai("gpt-3.5-turbo")


def parse_string_to_dialogues(dialogues_str: str) -> list[str]:
    dialogues_str = dialogues_str.strip()
    if not dialogues_str:
        return []
    dialogues_str = re.sub(r"\n+", "\n", dialogues_str)
    dialogues = [y.strip() for y in dialogues_str.split("\n")]
    size_arr = [tokenizer.length(y) for y in dialogues]
    dialogues = [
        "\n".join(x) for x in aggregate_with_overlaps(dialogues, size_arr, 150, 100)
    ]
    return dialogues


class ScrapedClone(BaseModel):
    name: str
    short_description: str
    long_description: str | dict[str, str]
    greeting: str
    avatar_uri: str
    scrape_source: str
    scenario: str | None
    example_dialogues: str | None
    tags: list[str] | None = None
    creator: str | None = None
    num_messages: int | None = None
    num_conversations: int | None = None
    created_at: int | None = None
    metadata: dict[str, Any] | None = None

    @classmethod
    def from_character_ai(cls, data: dict[str, Any]):
        tags = [x["name"] for x in data["categories"]]
        used_cols = set(
            [
                "name",
                "title",
                "description",
                "avatar_file_name",
                "definition",
                "user__username",
                "num_msgs",
                "categories",
            ]
        )
        metadata = {k: v for k, v in data.items() if k not in used_cols}
        return cls(
            name=data["name"],
            short_description=data["title"],
            long_description=data["description"],
            avatar_uri=data["avatar_file_name"],
            scenario=None,
            greeting=data["greeting"],
            example_dialogues=data["definition"],
            tags=tags,
            creator=data["user__username"],
            num_messages=data["num_interactions"],
            created_at=None,
            metadata=metadata,
            scrape_source="character_ai",
        )

    @classmethod
    def from_charstar_ai(cls, data: dict[str, Any]):
        long_description = dict(
            about=data["about"],
            **{
                k: v
                for k, v in data["metadata"].items()
                if k not in ["scenario", "exampleDialogue"]
            },
        )
        used_cols = set(
            ["name", "title", "about", "photoUri", "greeting", "metadata", "total"]
        )
        metadata = {k: v for k, v in data.items() if k not in used_cols}
        return cls(
            name=data["name"],
            short_description=data["title"],
            long_description=long_description,
            avatar_uri=data["photoUri"],
            greeting=data["greeting"],
            scenario=data["metadata"].get("scenario"),
            example_dialogues=data["metadata"].get("exampleDialogue"),
            tags=[x["name"] for x in data["tags"]],
            creator=None,  # TODO check if that's true
            num_messages=data["total"] // 1000,
            num_conversations=None,
            created_at=None,
            metadata=metadata,
            scrape_source="charstar",
        )

    @classmethod
    def from_janitor_ai(cls, data: dict[str, Any]):
        used_cols = set(
            [
                "name",
                "description",
                "personality",
                "first_message",
                "avatar",
                "scenario",
                "example_dialogs",
                "tags",
                "creator_id",
                "total_message",
                "total_chat",
                "created_at",
            ]
        )
        metadata = {k: v for k, v in data.items() if k not in used_cols}

        created_at = data["created_at"]
        if len(created_at) < 32:
            s = "0" * (32 - len(created_at)) + "+"
            created_at = created_at.replace("+", s)

        return cls(
            name=data["name"],
            short_description=data["description"],
            long_description=data["personality"],
            greeting=data["first_message"],
            avatar_uri=data["avatar"],
            scenario=data["scenario"],
            example_dialogues=data["example_dialogs"],
            tags=[x["slug"] for x in data["tags"]],
            creator=data["creator_id"],
            num_messages=data["total_message"],
            num_conversations=data["total_chat"],
            created_at=int(datetime.fromisoformat(created_at).timestamp()),
            metadata=metadata,
            scrape_source="janitor",
        )

    @classmethod
    def from_spicychat_ai(cls, data: dict[str, Any]):
        used_cols = set(
            [
                "name",
                "title",
                "persona",
                "greeting",
                "avatar_uri",
                "scenario",
                "dialogue",
                "tags",
                "creator_user_id",
                "num_messages",
                "created_at",
            ]
        )
        metadata = {k: v for k, v in data.items() if k not in used_cols}
        return cls(
            name=data["name"],
            short_description=data["title"],
            long_description=data["persona"],
            greeting=data["greeting"],
            avatar_uri=data["avatar_url"],
            scenario=data["scenario"] or None,
            example_dialogues=data["dialogue"] or None,
            tags=data["tags"] or [],
            creator=data["creator_user_id"],
            num_messages=data["num_messages"],
            num_conversations=None,
            created_at=int(data["createdAt"]),
            metadata=metadata,
            scrape_source="spicychat",
        )

    @classmethod
    def from_botprompts(cls, data: dict[str, Any]):
        long_description = {}
        if description := data.get("description"):
            long_description["description"] = description

        if char_persona := data.get("char_persona"):
            long_description["char_persona"] = char_persona

        if char_Persona := data.get("char_Persona"):
            long_description["char_persona"] = char_Persona

        if personality := data.get("personality"):
            long_description["personality"] = personality

        if properties := data.get("properties"):
            long_description["properties"] = properties

        if isinstance(long_description, dict):
            if "properties" in long_description:
                tmp = ""
                print(long_description["properties"])
                for k, v in long_description["properties"].items():
                    tmp += f"{k}: " + ", ".join(v) + "\n"
                    print(tmp)
                tmp = tmp.rstrip()
                long_description = tmp

        example_dialogues = data.get("example_dialogue", "") or ""
        example_dialogues = example_dialogues.replace("<START>", "\n\n")
        example_dialogues = re.sub(r"\nYou:", "\n{{user}}", example_dialogues)
        example_dialogues = re.sub(r"\n\w+:", "\n{{char}}", example_dialogues)

        short_description = data["char_name"]
        if universe := data["universe"]:
            short_description += " from " + re.sub(
                "\s+", " ", universe.replace("NSFW", "").replace("-", "")
            )

        greeting = data.get("char_greeting", data.get("first_mes"))
        if greeting is None:
            print(data)

        return cls(
            name=data["char_name"],
            short_description=short_description,
            long_description=long_description,
            greeting=greeting,
            avatar_uri="",
            scenario=data["world_scenario"],
            example_dialogues=example_dialogues,
            tags=[data["tag"]],
            creator=data["creator"],
            num_messages=None,
            num_conversations=None,
            created_at=None,
            metadata=None,
            scrape_source="botprompts",
        )

    @classmethod
    def from_chub_ai(cls, data: dict[str, Any]):
        scenario = data.get("scenario", "")

        if sys_prompt := data.get("system_prompt"):
            scenario += "\n" + sys_prompt

        if post_hist := data.get("post_history_instructions"):
            scenario += "\n" + post_hist

        if not scenario:
            scenario = None

        example_dialogues = data["example_dialogs"]
        example_dialogues = example_dialogues.replace("<START>", "")

        created_at = data["createdAt"].replace("Z", "")

        return cls(
            name=data["name"],
            short_description=data["tagline"],
            long_description=data["personality"],
            greeting=data["first_message"],
            avatar_uri=data["avatar"],
            scenario=scenario,
            example_dialogues=example_dialogues,
            tags=[x.lower() for x in data["topics"]],
            creator=data["maybe_creator"],
            num_messages=data["nChats"],
            num_conversations=data["nMessages"],
            created_at=int(datetime.fromisoformat(created_at).timestamp()),
            scrape_source="chub",
            metadata={
                "wilson_score": data["wilson_score"],
                "lorebooks": data["related_lorebooks"],
                "starCount": data["starCount"],
                "homepage_id": data["homepage_id"],
            },
        )


def clean_botprompts(path: str = "scraped_chars/botprompts.json") -> pd.DataFrame:
    df = pd.read_json(path)
    df = df[df.char_name != "Pandora’s Actor"]
    df = df[~(df.char_greeting.isna() & df.first_mes.isna())]
    data = df.progress_apply(
        lambda x: ScrapedClone.from_botprompts(x).model_dump(), axis=1
    ).to_list()
    return pd.DataFrame(data)


def clean_character_ai(
    path: str = "scraped_chars/characterai_chars.json",
) -> pd.DataFrame:
    df = pd.read_json(path)
    df = pd.DataFrame(df[df.status.isna()].character.to_list())
    data = df.progress_apply(
        lambda x: ScrapedClone.from_character_ai(x).model_dump(), axis=1
    ).to_list()
    return pd.DataFrame(data)


def clean_charstar() -> pd.DataFrame:
    data: list[dict] = []
    for s in ["", "n"]:
        path = f"scraped_chars/charstar_chars/charstarai_chars_{s}sfw.json"
        df = pd.read_json(path)
        path = f"scraped_chars/charstar_chars/charstarai_chars_{s}sfw_info.json"
        df_info = pd.read_json(path)
        df = df_info.merge(df, left_on="id", right_on="id", suffixes=("_left", ""))
        cur = df.progress_apply(
            lambda x: ScrapedClone.from_charstar_ai(x).model_dump(), axis=1
        ).to_list()
        data.extend(cur)
    return pd.DataFrame(data)


def clean_janitor(path: str = "scraped_chars/janitorai_chars") -> pd.DataFrame:
    df = pd.concat([pd.read_json(os.path.join(path, x)) for x in os.listdir(path)])
    df = pd.DataFrame(df.data.to_list())
    data = df.progress_apply(
        lambda x: ScrapedClone.from_janitor_ai(x).model_dump(), axis=1
    ).to_list()
    return pd.DataFrame(data)


def clean_spicychat(path: str = "scraped_chars/spicychat_chars.json") -> pd.DataFrame:
    df = pd.read_json(path)
    df["dialogue"] = df.dialogue.fillna("")
    df["scenario"] = df.scenario.fillna("")
    df["tags"] = df.tags.fillna("")
    data = df.progress_apply(
        lambda x: ScrapedClone.from_spicychat_ai(x).model_dump(), axis=1
    ).to_list()
    return pd.DataFrame(data)


def clean_chub_ai(path: str = "scraped_chars/chub.json") -> pd.DataFrame:
    tmp = pd.read_json(path)
    cols = [k for k in tmp if k != "definition"]
    df = pd.DataFrame(tmp.definition.to_list())
    for k in cols:
        if k not in df.columns:
            df[k] = tmp[k]
    data = df.progress_apply(
        lambda x: ScrapedClone.from_chub_ai(x).model_dump(), axis=1
    ).to_list()
    return pd.DataFrame(data)


def clean_everything() -> pd.DataFrame:
    return pd.concat(
        [
            clean_botprompts(),
            clean_character_ai(),
            clean_charstar(),
            clean_chub_ai(),
            clean_janitor(),
            clean_spicychat(),
        ]
    )
