import logging
import datetime
from os import path, makedirs
from urllib.parse import urljoin
from typing import Tuple, List
from time import sleep

from link_scraper import scrape_quiz_links
from paywall_bypasser import bypass_paywall
from quiz_html_parser import extract_question_answer_pairs


LOGGER = logging.getLogger()
PRODUCT_PATH = "Product"
EXCLUDED_LIST_PATH = path.join(PRODUCT_PATH, "excluded_list.txt")
EXCLUDED_LIST_DELIMITER = "\n"
BASE_SITE_URL = "https://www.haaretz.co.il"
TIME_TO_SLEEP = 0.3
NUMBER_OF_QUIZES = 400


def setup_logger():
    LOGGER.setLevel(logging.DEBUG)
    error_log = logging.FileHandler("error.log")
    info_log = logging.FileHandler("info.log")
    debug_log = logging.FileHandler("debug.log")
    error_log.setLevel(logging.ERROR)
    info_log.setLevel(logging.INFO)
    debug_log.setLevel(logging.DEBUG)
    formatter = logging.Formatter("%(asctime)s - %(name)s - %(levelname)s - %(message)s")
    error_log.setFormatter(formatter)
    info_log.setFormatter(formatter)
    debug_log.setFormatter(formatter)
    LOGGER.addHandler(error_log)
    LOGGER.addHandler(info_log)
    LOGGER.addHandler(debug_log)


def add_quiz_to_excluded_list(quiz_url):
    quiz_id = quiz_url.split('/')[-1]
    LOGGER.debug(f"Adding quiz id \"{quiz_id}\" to excluded list")

    with open(EXCLUDED_LIST_PATH, "a") as f:
        f.write(quiz_id + EXCLUDED_LIST_DELIMITER)


def save_quiz_info(quiz_date: datetime.datetime, quiz_url: str, full_quiz: List[Tuple[str, str]]):
    LOGGER.debug(f"Saving quiz: {quiz_url}")
    quiz_id = quiz_url.split('/')[-1]
    LOGGER.debug(f"into: \"{quiz_date.date()} - {quiz_id}.txt\"")

    with open(path.join(PRODUCT_PATH, f"{quiz_date.date()} - {quiz_id}.txt"), "wb") as f:
        for q, a in full_quiz:
            f.write(f"Q: {q}\nA: {a}\n\n".encode())
    LOGGER.debug("Saved quiz")


def main():
    setup_logger()
    start_time = datetime.datetime.now()
    LOGGER.info(f"Started Scraping. Start Time: {start_time}")

    try:
        if not path.exists(PRODUCT_PATH):
            makedirs(PRODUCT_PATH)
            LOGGER.debug("Created Product dir")

        LOGGER.info("Scraping for quiz links")
        for index, (quiz_url, quiz_date) in enumerate(
            scrape_quiz_links(
                number_of_links=NUMBER_OF_QUIZES,
                excluded_list_path=EXCLUDED_LIST_PATH,
                excluded_list_delimiter=EXCLUDED_LIST_DELIMITER,
            )
        ):
            LOGGER.info(f"Started scraping quiz number {index + 1}/{NUMBER_OF_QUIZES}. Operating for {datetime.datetime.now() - start_time}")

            LOGGER.info(f"Bypassing paywall for quiz {quiz_url}")
            quiz_soup = bypass_paywall(urljoin(BASE_SITE_URL, quiz_url))

            full_quiz = extract_question_answer_pairs(quiz_soup)
            if not full_quiz:
                LOGGER.error(f"Quiz {quiz_url} is empty!")
                add_quiz_to_excluded_list(quiz_url)
                LOGGER.info(f"Sleeping for {TIME_TO_SLEEP} seconds...")
                sleep(TIME_TO_SLEEP)
                continue
            LOGGER.info(f"Parsed quiz - found {len(full_quiz)} questions")

            LOGGER.info(f"Saving quiz")
            save_quiz_info(quiz_date, quiz_url, full_quiz)

            add_quiz_to_excluded_list(quiz_url)
            LOGGER.info(f"Sleeping for {TIME_TO_SLEEP} seconds...")
            sleep(TIME_TO_SLEEP)

        LOGGER.info("Finished successfully")

    except Exception:
        LOGGER.exception("Encountered an exception:")
        raise


if __name__ == "__main__":
    main()
