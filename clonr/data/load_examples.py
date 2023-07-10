import re
from functools import lru_cache
from pathlib import Path

from clonr.data_structures import Dialogue, DialogueMessage


@lru_cache(maxsize=None)
def load_lebron_data():
    path = Path(__file__).parent / "assets" / "lebron-wiki.txt"
    with open(path, "r") as f:
        return f.read()


@lru_cache(maxsize=None)
def load_paul_graham_data():
    path = Path(__file__).parent / "assets" / "paul-graham-essay.txt"
    with open(path, "r") as f:
        return f.read()


@lru_cache(maxsize=None)
def load_makima_data():
    path = Path(__file__).parent / "assets" / "makima.txt"
    with open(path, "r") as f:
        return f.read()


@lru_cache(maxsize=None)
def load_makima_short_description() -> str:
    path = Path(__file__).parent / "assets" / "makima" / "short_description.txt"
    with open(path, "r") as f:
        return f.read()


@lru_cache(maxsize=None)
def load_makima_long_description() -> str:
    path = Path(__file__).parent / "assets" / "makima" / "long_description.txt"
    with open(path, "r") as f:
        return f.read()


@lru_cache(maxsize=None)
def load_makima_greeting_message() -> str:
    path = Path(__file__).parent / "assets" / "makima" / "greeting_message.txt"
    with open(path, "r") as f:
        return f.read()


@lru_cache(maxsize=None)
def load_makima_example_dialogues() -> list[Dialogue]:
    path = Path(__file__).parent / "assets" / "makima" / "dialogues.txt"
    with open(path, "r") as f:
        s = f.read()

    dialogues: list[Dialogue] = []
    messages: list[DialogueMessage] = []

    # (Jonny): This part is just specific to how we stored dialogues. Really need to figure this out
    for d in s.split("### Dialogue\n"):
        if not d:
            continue
        char = "Makima"
        dialogue = Dialogue(source="manual")
        pattern = r"(\w+): (.*?)(?=\n|$)"
        matches = re.findall(pattern, d, re.DOTALL)
        for i, match in enumerate(matches):
            msg = DialogueMessage(
                sender_name=match[0],
                content=match[1],
                index=i,
                dialogue_id=dialogue.id,
                is_clone=match[0].lower() == char.lower(),
            )
            messages.append(msg)
            dialogue.message_ids.append(msg.id)
            dialogue.messages.append(msg)
        dialogues.append(dialogue)
        # hack to reset the hash and not screw up the above dependencies
    return dialogues
