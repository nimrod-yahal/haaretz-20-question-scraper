import logging
from typing import Tuple, List
from bs4 import BeautifulSoup


LOGGER = logging.getLogger(__name__)
QUESTION_STYLE = "background-repeat:no-repeat;font-size:24px;font-weight:700;box-sizing:border-box;display:block;line-height:30px;margin-bottom:42px;"
ANSWER_STYLE = "background-repeat:no-repeat;font-size:18px;box-sizing:border-box;display:block;line-height:24px;margin-bottom:18px;"


def extract_question_answer_pairs(soup: BeautifulSoup) -> List[Tuple[str, str]]:
    question_tags = soup.find_all(lambda tag: tag.text and "style" in tag.attrs and tag.attrs["style"] == QUESTION_STYLE)
    LOGGER.debug(f"Questions: {[q.text for q in question_tags]}")
    answer_tags = soup.find_all(lambda tag: tag.text and "style" in tag.attrs and tag.attrs["style"] == ANSWER_STYLE)
    LOGGER.debug(f"Answers: {[a.text for a in answer_tags]}")

    return [(q.text, a.text) for q, a in zip(question_tags, answer_tags)]
