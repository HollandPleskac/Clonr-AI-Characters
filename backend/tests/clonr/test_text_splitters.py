import textwrap

import pytest

from clonr.text_splitters import (
    CharSplitter,
    SentenceSplitter,
    TokenSplitter,
    _is_asian_language,
    _is_english,
    regex_split,
)
from clonr.tokenizer import _get_tiktoken_tokenizer


@pytest.fixture
def corpus():
    return textwrap.dedent(
        """
        LeBron James
        LeBron Raymone James Sr. (/ləˈbrɒn/ lə-BRON; born December 30, 1984) is an American professional basketball player for the Los Angeles Lakers of the National Basketball Association (NBA). Nicknamed "King James", he is widely regarded as one of the greatest players in the history of the sport and is often compared to Michael Jordan in debates over the greatest basketball player of all time.[a] James is the all-time leading scorer in NBA history and ranks fourth in career assists. He has won four NBA championships (two with the Miami Heat, one each with the Lakers and Cleveland Cavaliers), and has competed in 10 NBA Finals. He has also won four Most Valuable Player (MVP) Awards, four Finals MVP Awards, and two Olympic gold medals, and has been named an All-Star 19 times, selected to the All-NBA Team 19 times (including 13 First Team selections) and the All-Defensive Team six times, and was a runner-up for the NBA Defensive Player of the Year Award twice in his career.
        James grew up playing basketball for St. Vincent–St. Mary High School in his hometown of Akron, Ohio. He was heavily touted by the national media as a future NBA superstar. A prep-to-pro, he was selected by the Cleveland Cavaliers with the first overall pick of the 2003 NBA draft. Named the 2004 NBA Rookie of the Year, he soon established himself as one of the league's premier players, leading the Cavaliers to their first NBA Finals appearance in 2007 and winning the NBA MVP award in 2009 and 2010. After failing to win a championship with Cleveland, James left in 2010 as a free agent to join the Miami Heat; this was announced in a nationally televised special titled The Decision and is among the most controversial free agency moves in sports history.
        James won his first two NBA championships while playing for the Heat in 2012 and 2013; in both of these years, he also earned the league's MVP and Finals MVP awards. After his fourth season with the Heat in 2014, James opted out of his contract and re-signed with the Cavaliers. In 2016, he led the Cavaliers to victory over the Golden State Warriors in the Finals by coming back from a 3–1 deficit, delivering the team's first championship and ending the Cleveland sports curse. In 2018, James exercised his contract option to leave the Cavaliers and signed with the Lakers, where he won the 2020 NBA championship and his fourth Finals MVP. James is the first player in NBA history to accumulate $1 billion in earnings as an active player. On February 7, 2023, James surpassed Kareem Abdul-Jabbar to become the all-time leading scorer in NBA history.
        Off the court, James has accumulated more wealth and fame from numerous endorsement contracts. He has been featured in books, documentaries (including winning three Sports Emmy Awards as an executive producer), and television commercials. He has won 19 ESPY Awards, hosted Saturday Night Live, and starred in the sports film Space Jam: A New Legacy (2021). James has been a part-owner of Liverpool F.C. since 2011 and leads the LeBron James Family Foundation, which has opened an elementary school, housing complex, retail plaza, and medical center in Akron.
        Early life
        James was born on December 30, 1984, in Akron, Ohio, to Gloria Marie James, who was 16 at the time of his birth.: 22 His father, Anthony McClelland, has an extensive criminal record and was not involved in his life. When James was growing up, life was often a struggle for the family, as they moved from apartment to apartment in the seedier neighborhoods of Akron while Gloria struggled to find steady work. Realizing that her son would be better off in a more stable family environment, Gloria allowed him to move in with the family of Frank Walker, a local youth football coach who introduced James to basketball when he was nine years old.: 23
        James began playing organized basketball in the fifth grade. He later played Amateur Athletic Union (AAU) basketball for the Northeast Ohio Shooting Stars. The team enjoyed success on a local and national level, led by James and his friends Sian Cotton, Dru Joyce III, and Willie McGee.: 24 The group dubbed themselves the "Fab Four" and promised each other that they would attend high school together.: 27 In a move that stirred local controversy, they chose to attend St. Vincent–St. Mary High School, a private Catholic school with predominantly white students."""
    )


def test_language_heuristics():
    assert not _is_asian_language("привет, меня зовут Джонни")
    assert not _is_asian_language("hola como está?")
    assert not _is_english("привет, меня зовут Джонни")
    assert _is_english("hi how are you?")
    assert _is_asian_language("我做出了可怕的人生选择, lol this is chinese")
    assert not _is_english("hola como está?")


def test_regex_split():
    s = "foo. bar!?! and baz... ok."
    r = ["foo.", " bar!?!", " and baz...", " ok."]
    assert regex_split(s, r"[\?\!\.]+", True) == r
    assert regex_split(s, r"[\?\!\.]+", False) == ["foo", " bar", " and baz", " ok"]


@pytest.mark.parametrize("overlap", [0])
@pytest.mark.parametrize("size", [128])
def test_splitters(corpus, size, overlap):
    splitter = SentenceSplitter(max_chunk_size=size, min_chunk_size=0, overlap=overlap)
    arr = splitter.split(corpus)
    assert len(arr) > 1
    assert len(corpus) - 500 < sum(map(len, arr)) < len(corpus) + 500

    tokenizer = _get_tiktoken_tokenizer("gpt-3.5-turbo")
    splitter = TokenSplitter(
        tokenizer=tokenizer, chunk_size=size, chunk_overlap=overlap
    )
    arr = splitter.split(corpus)
    assert len(arr) > 1
    assert len(corpus) - 500 < sum(map(len, arr)) < len(corpus) + 500

    splitter = CharSplitter(chunk_size=size, chunk_overlap=overlap)
    arr = splitter.split(corpus)
    assert len(arr) > 1
    assert len(corpus) - 500 < sum(map(len, arr)) < len(corpus) + 500
