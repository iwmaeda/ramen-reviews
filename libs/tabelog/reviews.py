import time

import requests
from bs4 import BeautifulSoup


class TabelogReviews(object):
    def __init__(self):
        self.ok = False
        self.reviewer_url = 'unknown'
        self.review_title = 'unknown'
        self.review_text = 'unknown'
        self.review_contents = ['reviewer_url', 'review_title', 'review_text']

    def input_retrieved_reviews(self, reviewer_url=None, review_title=None, review_text=None):
        self.ok = True
        if reviewer_url is not None:
            self.reviewer_url = reviewer_url
        if review_title is not None:
            self.review_title = review_title
        if review_text is not None:
            self.review_text = review_text
        return self

    def output_retrieved_reviews(self, contents=None):
        if contents is None:
            contents = self.review_contents
        # Get reviews
        dict_reviews = {}
        for c in contents:
            if hasattr(self, c):
                dict_reviews[c] = getattr(self, c)
        return dict_reviews


def resp_to_soup(resp):
    try:
        soup = BeautifulSoup(resp.text, 'lxml')
    except:
        soup = BeautifulSoup(resp.text, 'html5lib')
    return soup


def get_review_text(resp):
    if resp.ok is True:
        soup = resp_to_soup(resp)

        # Reviewer URL
        try:
            reviewer_url = soup.find('p', class_='rvw-item__rvwr-name auth-mobile').find('a', target='_blank')['href']
        except:
            reviewer_url = 'unknown'

        # Review score
        # Implemented

        # Review title
        try:
            review_title = soup.find('p', class_='rvw-item__title').get_text(strip=True)
        except:
            review_title = 'unknown'

        # Review text
        try:
            review_text = soup.find('div', class_='rvw-item__rvw-comment').find('p').get_text(strip=True)
        except:
            review_text = 'unknown'

        return TabelogReviews().input_retrieved_reviews(
            reviewer_url=reviewer_url, review_title=review_title, review_text=review_text)
    else:
        return TabelogReviews()


def get_review_pages_from_restaurant_page(url, interval=1):
    url_review_page = url + 'dtlrvwlst/'

    list_review_pages = []
    while True:
        resp = requests.get(url_review_page)
        if resp.ok is True:
            soup = resp_to_soup(resp)

            list_review_pages += ['https://tabelog.com' + item['href'] for item
                                  in soup.find_all('a', class_='rvw-item__title-target')]

            # Get next url
            if soup.find('a', class_='c-pagination__arrow c-pagination__arrow--next') is not None:
                url_review_page = 'https://tabelog.com' + soup.find(
                    'a', class_='c-pagination__arrow c-pagination__arrow--next')['href']
            else:
                break
        else:
            break

        # Sleep
        time.sleep(interval)

    return list_review_pages


def get_restaurant_pages_from_search_result(url, interval=1):
    list_restaurant_pages = []
    while True:
        resp = requests.get(url)
        if resp.ok is True:
            soup = resp_to_soup(resp)

            list_restaurant_pages += [item['href'] for item
                                      in soup.find_all('a', class_='list-rst__rst-name-target cpy-rst-name')]

            # Get next url
            if soup.find('a', class_='c-pagination__arrow c-pagination__arrow--next') is not None:
                url = 'https://tabelog.com' + soup.find(
                    'a', class_='c-pagination__arrow c-pagination__arrow--next')['href']
            else:
                break
        else:
            break

        # Sleep
        time.sleep(interval)

    return list_restaurant_pages
