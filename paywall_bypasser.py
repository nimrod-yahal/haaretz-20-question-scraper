import logging
import requests
from bs4 import BeautifulSoup


LOGGER = logging.getLogger(__name__)
ARCHIVE_TODAY_BASE_URL = "https://archive.md/"

STANDARD_USER_AGENT = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/93.0.4577.82 Safari/537.36"
BYPASSING_USER_AGENT = "Mozilla/5.0(Java) outbrain"

STANDARD_HEADERS = {
    "User-Agent": STANDARD_USER_AGENT,
}
BYPASSING_HEADERS = {
    "User-Agent": BYPASSING_USER_AGENT,
}

ARCHIVED_LINKS_TAG_STYLE = "display:block;color:blue;font-size:16px;word-break:break-word"


def _bypass_haaretz_user_agent_check(url: str) -> BeautifulSoup:
    response = requests.get(url, headers=BYPASSING_HEADERS)
    return BeautifulSoup(response.text, features="html.parser")


def bypass_paywall(url: str) -> BeautifulSoup:
    LOGGER.debug(f"Bypassing paywall for {url}")

    LOGGER.debug(f"Searching for archived quiz in {ARCHIVE_TODAY_BASE_URL + url}")
    response = requests.get(ARCHIVE_TODAY_BASE_URL + url, headers=STANDARD_HEADERS)
    LOGGER.debug(f"Received {response}")
    archive_today_soup = BeautifulSoup(response.text, features="html.parser")

    archived_link_tag = archive_today_soup.find(lambda tag: tag.name=="a" and tag.text and tag.attrs.get("style")==ARCHIVED_LINKS_TAG_STYLE)
    if archived_link_tag is None:
        LOGGER.debug(f"Quiz URL {url} is not found in the archive, attempting direct bypass using user-agent shananigans")
        return _bypass_haaretz_user_agent_check(url)
    LOGGER.debug(f"Found archived quiz: {archived_link_tag['href']}")

    response = requests.get(archived_link_tag["href"], headers=STANDARD_HEADERS)
    return BeautifulSoup(response.text, features="html.parser")
