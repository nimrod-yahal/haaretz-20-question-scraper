# coding: utf-8
import requests
import json
from bs4 import BeautifulSoup, SoupStrainer
from urllib.parse import urljoin


LINK_SCRAPING_URL = 'https://graphql.haaretz.co.il:443/'
LINK_SCRAPING_HEADERS = {
	'Hostname': 'www.haaretz.co.il', 
	'User-Agent': 'msnbot/0.3 (+http://search.msn.com/msnbot.htm)', 
	'Content-Type': 'application/json'
}
LINK_SCRAPING_QUERY = 'query TateQuery($input: ListInput!) {\n list(input: $input) {\n items {\n ... on Teaser {\n path\n}\n}\n}\n}\n'

BASE_URL = 'https://www.haaretz.co.il/magazine/20questions/'
HEADERS = {'User-Agent': 'msnbot/0.3 (+http://search.msn.com/msnbot.htm)'}
QUESTIONS_CLASS = 'ps pt pu ju jv pv pw'
ANSWERS_CLASS = 'qy qz ra rb rc rd re rf rg rh ri rj'


def scrape_test_links(max_page_index):
	links = []

	for index in range(max_page_index + 1):
		query_json = {
			'operationName': 'TateQuery', 
			'variables': {
				'input': {
					'history': [], 
					'listId': '7.9658724', 
					'pageIndex': index,
					'sectionId': '2.788'
				}
			},
			'query': LINK_SCRAPING_QUERY
		}
		response = requests.post(LINK_SCRAPING_URL, headers=LINK_SCRAPING_HEADERS, json=query_json)

		links.extend([item['path'] for item in json.loads(response.text)['data']['list']['items']])
	return links


def get_test_data(test_link):
	url = urljoin(BASE_URL, test_link)

	response = requests.get(url, headers=HEADERS)
	parsed_html = BeautifulSoup(response.text)

	questions = parsed_html.body.find_all('div', attrs={'class': QUESTIONS_CLASS})
	answers = parsed_html.body.find_all('div', attrs={'class': ANSWERS_CLASS})

	stripped_questions = [div.text for div in questions]
	stripped_answers = [div.text for div in answers]

	return list(zip(stripped_questions, stripped_answers))


def main():
	tests_data = []
	for test_url in scrape_test_links(10):
		test_data = get_test_data(test_url)
		tests_data.extend(test_data)
	return tests_data
