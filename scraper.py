# coding: utf-8
import requests
import json
import logging
import os
from bs4 import BeautifulSoup, SoupStrainer
from urllib.parse import urljoin
from os import path


PRODUCT_PATH = 'Product'

LINK_SCRAPING_URL = 'https://graphql.haaretz.co.il:443/'
LINK_SCRAPING_HEADERS = {
	'Hostname': 'www.haaretz.co.il', 
	'User-Agent': 'msnbot/0.3 (+http://search.msn.com/msnbot.htm)', 
	'Content-Type': 'application/json'
}
LINK_SCRAPING_QUERY = 'query TateQuery($input: ListInput!) {\n list(input: $input) {\n items {\n ... on Teaser {\n path\n}\n}\n}\n}\n'

BASE_URL = 'https://www.haaretz.co.il/magazine/20questions/'
HEADERS = {'User-Agent': 'msnbot/0.3 (+http://search.msn.com/msnbot.htm)'}
EXPECTED_QUESTIONS_COUNT_PER_TEST = 21


def scrape_test_links(max_page_index):
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

		for link in [item['path'] for item in json.loads(response.text)['data']['list']['items']]:
			yield link


def get_question_answer_pair(parsed_html, question_index):
	parent_div = parsed_html.find_all(attrs={'data-test':f'question-slide-{question_index}'})[0]

	# Performs the div voodoo-navigation to find the question and answer texts
	question = list(list(parent_div.children)[0].children)[1].text
	answer = list(list(parent_div.children)[1].children)[0].text

	return question, answer


def get_test_data(test_link):
	url = urljoin(BASE_URL, test_link)

	response = requests.get(url, headers=HEADERS)
	parsed_html = BeautifulSoup(response.text, features='html.parser')

	return [get_question_answer_pair(parsed_html, index) for index in range(1, 22)]


def dump_test_data(test_data, test_url_name):
	with open(path.join(PRODUCT_PATH, f'{test_url_name}.txt'), 'w') as f:
		for q, a in test_data:
			f.write(f'Q: {q}\nA: {a}\n\n')


def add_failure(test_url, error_message):
	logging.error(f'{error_message} on test url: {test_url}')
	with open(path.join(PRODUCT_PATH, 'failed-urls.txt'), 'a') as f:
		f.write(f'{error_message}: \t{urljoin(BASE_URL, test_url)}\n')


def main():
	logger = logging.getLogger()
	logger.setLevel(logging.INFO)

	if not path.exists(PRODUCT_PATH):
		os.makedirs(PRODUCT_PATH)

	for test_url in scrape_test_links(15):
		test_url_name = test_url.split('/')[-1]

		with open(path.join(PRODUCT_PATH, 'index.txt'), 'a') as f:
			f.write(f'{test_url_name}\n')

		logging.info(f'Scraping test url: {test_url_name}')
		test_data = get_test_data(test_url)
		if len(test_data) < EXPECTED_QUESTIONS_COUNT_PER_TEST:
			add_failure(test_url, 'Anomalous HTML')
		else:
			try:
				dump_test_data(test_data, test_url_name)
			except:
				add_failure(test_url, 'EXCEPTION')


if __name__ == '__main__':
	main()
