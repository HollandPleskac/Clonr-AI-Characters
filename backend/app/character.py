import json
import logging

from loguru import logger
from tenacity import (
    after_log,
    before_sleep_log,
    retry,
    retry_if_exception,
    stop_after_attempt,
    wait_none,
)

from app import models
from clonr.llms import OpenAI

MAX_RETRIES = 2

CHAR = "Barack Obama"
USER = "User"

INITIAL_MESSAGE = (
    "Hey now, I've talked to folks all over this country but I haven't talked to you."
)

EXAMPLE_DIALOGUES = """\
Change will not come if we wait for some other person or some other time. We are the ones we've been waiting for. We are the change that we seek.
The future rewards those who press on. I don't have time to feel sorry for myself. I don't have time to complain. I'm going to press on.
There is not a liberal America and a conservative America - there is the United States of America. There is not a black America and a white America and latino America and asian America - there's the United States of America.
We need to internalize this idea of excellence. Not many folks spend a lot of time trying to be excellent.\
""".split(
    "\n"
)


CHAR_DESC = """Barack H. Obama is the 44th President of the United States.
His story is the American story — values from the heartland, a middle-class upbringing in a strong family, hard work and education as the means of getting ahead, and the conviction that a life so blessed should be lived in service to others.
With a father from Kenya and a mother from Kansas, President Obama was born in Hawaii on August 4, 1961. He was raised with help from his grandfather, who served in Patton's army, and his grandmother, who worked her way up from the secretarial pool to middle management at a bank.
After working his way through college with the help of scholarships and student loans, President Obama moved to Chicago, where he worked with a group of churches to help rebuild communities devastated by the closure of local steel plants.
He went on to attend law school, where he became the first African-American president of the Harvard Law Review. Upon graduation, he returned to Chicago to help lead a voter registration drive, teach constitutional law at the University of Chicago, and remain active in his community.
President Obama's years of public service are based around his unwavering belief in the ability to unite people around a politics of purpose. In the Illinois State Senate, he passed the first major ethics reform in 25 years, cut taxes for working families, and expanded health care for children and their parents. As a United States Senator, he reached across the aisle to pass groundbreaking lobbying reform, lock up the world's most dangerous weapons, and bring transparency to government by putting federal spending online.
"""


def create_prompt(
    facts: list[str],
    past_msgs: list[models.Message],
    current_msgs: list[models.Message],
    char: str = CHAR,
    char_desc: str = CHAR_DESC,
    example_dialogues: list[str] = EXAMPLE_DIALOGUES,
    user: str = USER,
):
    tmpl = """\
<|im_start|>system
You are a helpful AI assistant who exactly follows instructions.
<|im_end|>

<|im_start|>user
You are chatting with a {user}, playing the role of {char}. You perfectly imitate {char}.
Respond only as {char}, and never break character. {char} can be described as follows:
{char_desc}

Here are some example dialogues that elucidate {char}'s speech and chat patterns:

{example_dialogues}

Here are list of facts about {char} that may be relevant to playing the role of {char}:
{facts}

Finally, here is a list of past messages between {char} and {user} that may be relevant to the
current conversation:
{past_msgs}

Let's now have a conversation with you as {char} and me as {user}.
<|im_end|>

{current_msgs}
"""
    example_dialogues = "\n".join([f"{char}: {x}" for x in example_dialogues])
    facts = "\n".join([f"{i+1}: {x}" for i, x in enumerate(facts)])
    past_msgs = "\n".join([f"{x.sender_name}: {x.content}" for x in past_msgs])
    current_msgs_: list[str] = []
    for x in current_msgs:
        if x.sender_name == char:
            y = f"<|im_start|>assistant\n{x.content}<|im_end|>"
        elif x.sender_name == user:
            y = f"<|im_start|>user\n{x.content}<|im_end|>"
        else:
            raise ValueError(f"Invalid sender name: {x.sender_name}")
        current_msgs_.append(y)
    current_msgs = "\n".join(current_msgs_)
    prompt = tmpl.format(
        char=char,
        char_desc=char_desc,
        example_dialogues=example_dialogues,
        facts=facts,
        past_msgs=past_msgs,
        current_msgs=current_msgs,
        user=user,
    )
    return prompt


def create_message_query_prompt(
    messages: list[str], char: str = CHAR, user: str = USER
):
    tmpl = """\
<|im_start|>system
You are a helpful AI assistant who exactly follows instructions.
<|im_end|>

<|im_start|>user
You have access to a database of information about {char}, as well as \
access to all past messages between {char} and {user}. Consider the following \
recent messages between {char} and {user}:
{messages}

What are 3 question you would like answered in order to better predict the next \
message in this conversation? Return your output as in JSON format as a list of strings. \
An example output would be ["question 1", "question 2", "question 3"].
<|im_end|>

<|im_start|>assistant
[<|im_end|>"""
    message_str = "\n".join(f"{x.sender_name}: {x.content}" for x in messages)
    return tmpl.format(char=char, user=user, messages=message_str)


@retry(
    stop=stop_after_attempt(MAX_RETRIES),
    wait=wait_none(),
    retry=retry_if_exception(json.JSONDecodeError),
    before_sleep=before_sleep_log(logger, logging.INFO),
    after=after_log(logger, logging.WARN),
)
async def create_message_query(
    llm: OpenAI, db, messages: list[str], char: str = CHAR, user: str = "User"
) -> list[str]:
    prompt = create_message_query_prompt(messages=messages, char=char, user=user)
    logger.info("Attempting to generate message query.")
    # logger.warning(f"----\n\n\nPROMPT:\n{prompt}\n\n\n-----")
    # with open("logged_query_calls", "a") as f:
    #     f.write(f"-----\nPROMPT:\n{prompt}")
    r = await llm.agenerate(prompt, temperature=0.0)
    llm_call = models.LLMCall(
        content=r.content,
        prompt_tokens=r.usage.prompt_tokens,
        completion_tokens=r.usage.completion_tokens,
        total_tokens=r.usage.total_tokens,
        finish_reason=r.finish_reason,
        role=r.role,
        tokens_per_second=r.tokens_per_second,
        prompt=prompt,
    )
    db.add(llm_call)
    await db.commit()
    content = f"[{r.content}"
    # with open("logged_query_calls", "a") as f:
    #     f.write(f"-----\nQUERIES:\n{content}")
    # logger.warning(f"----\n\n\nQUERIES:\n{content}\n\n\n-----")
    try:
        return json.loads(content)
    except json.JSONDecodeError as e:
        res = content.split("\n")
        if len(res) == 3:
            return res
        else:
            return [content]
