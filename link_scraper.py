import datetime
import requests
import json
import logging
from typing import Generator, Tuple


LOGGER = logging.getLogger(__name__)
LINK_SCRAPING_URL = "https://graphql.haaretz.co.il/gql?operationName=TateListQuery"
GET_LINK_SCRAPING_QUERY_JSON = lambda exclude: {
    "operationName": "TateListQuery",
    "extensions": {
        "persistedQuery": {
            "sha256Hash": "45c471888ee377786c40bc7b18bc91d29862551a2a949f1fa507a9406a985943",
            "version": 1,
        },
    },
    "variables": {
        "exclude": ",".join(exclude),
        "id": "0000017e-05fa-d648-a57e-05fe8c2b0001",
        "mainContentId": "0000017d-d241-dcad-ab7d-dbff9d060000",
    },
}


def scrape_quiz_links(
    number_of_links: int = 12,
    excluded_list_path: str = "",
    excluded_list_delimiter: str = "\n",
) -> Generator[Tuple[str, datetime.datetime], None, None]:
    if excluded_list_path:
        with open(excluded_list_path, "r") as f:
            excluded_ids = f.read().strip(excluded_list_delimiter).split(excluded_list_delimiter)
    else:
        excluded_ids = []
    number_of_served = 0

    LOGGER.debug(f"Started scraping links for quizes, excluded: {excluded_ids}")
    while len(excluded_ids) < number_of_links:
        LOGGER.debug(f"Querying links from {LINK_SCRAPING_URL}")
        LOGGER.debug(f"excepting {excluded_ids}")
        response = requests.post(url=LINK_SCRAPING_URL, json=GET_LINK_SCRAPING_QUERY_JSON(excluded_ids))
        LOGGER.debug(f"Received: {response}")

        links = [
            (item["path"], datetime.datetime.fromtimestamp(item["publishDate"] / 1000))
            for item in json.loads(response.text)["data"]["List"]["items"]
        ]
        excluded_ids.extend([
            item["contentId"]
            for item in json.loads(response.text)["data"]["List"]["items"]
        ])
        LOGGER.debug(f"Links received: {links}")

        for link, published_date in links:
            if number_of_served < number_of_links:
                number_of_served += 1
                yield link, published_date
            else:
                return
