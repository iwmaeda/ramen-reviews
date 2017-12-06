import math
import time

import numpy as np
import pandas as pd
import requests
from bs4 import BeautifulSoup


class TabelogReviews(object):
    def __init__(self):
        self.ok = False
        self.restaurant_name = 'unknown'
        self.reviewer_url = 'unknown'
        self.review_ratings = {'dinner_overall': np.nan, 'dinner_taste': np.nan, 'dinner_service': np.nan,
                               'dinner_mood': np.nan, 'dinner_cp': np.nan, 'dinner_drink': np.nan,
                               'lunch_overall': np.nan, 'lunch_taste': np.nan, 'lunch_service': np.nan,
                               'lunch_mood': np.nan, 'lunch_cp': np.nan, 'lunch_drink': np.nan}
        self.review_title = 'unknown'
        self.review_text = 'unknown'
        self.review_contents = ['restaurant_name', 'reviewer_url',
                                'review_ratings', 'review_title', 'review_text']

    def input_retrieved_reviews(self, restaurant_name=None, reviewer_url=None,
                                review_ratings=None, review_title=None, review_text=None):
        self.ok = True
        if restaurant_name is not None:
            self.restaurant_name = restaurant_name
        if reviewer_url is not None:
            self.reviewer_url = reviewer_url
        if review_ratings is not None:
            if not isinstance(review_ratings, dict):
                ValueError('review_ratings must be dict')
            else:
                self.review_ratings = review_ratings
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
                if c == 'review_ratings':
                    dict_reviews.update(self.review_ratings)
                else:
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

        # Restaurant name
        restaurant_name = soup.find('div', class_='rdheader-rstname').find('span', property='').get_text(strip=True)

        # Reviewer URL
        tag_url = soup.find('p', class_='rvw-item__rvwr-name auth-mobile')
        if tag_url is not None:
            reviewer_url = tag_url.find('a', target='_blank')['href']
        else:
            reviewer_url = 'unknown'

        # Review ratings
        review_ratings = {'dinner_overall': np.nan, 'dinner_taste': np.nan, 'dinner_service': np.nan,
                          'dinner_mood': np.nan, 'dinner_cp': np.nan, 'dinner_drink': np.nan,
                          'lunch_overall': np.nan, 'lunch_taste': np.nan, 'lunch_service': np.nan,
                          'lunch_mood': np.nan, 'lunch_cp': np.nan, 'lunch_drink': np.nan}
        list_ratings = soup.find_all('li', class_='rvw-item__ratings-item u-clearfix')
        if list_ratings is not None:
            for r in list_ratings:
                if r.find('span', class_='c-rating__time c-rating__time--dinner') is not None:
                    # Dinner ratings
                    review_ratings['dinner_overall'] = float(r.find(
                        'b', class_='c-rating__val c-rating__val--strong').get_text(strip=True))
                    category_ratings = [np.nan if v.get_text(strip=True) == '-' else float(v.get_text(strip=True))
                                        for v in r.find_all('strong', class_='rvw-item__ratings-dtlscore-score')]
                    review_ratings['dinner_taste'] = category_ratings[0]
                    review_ratings['dinner_service'] = category_ratings[1]
                    review_ratings['dinner_mood'] = category_ratings[2]
                    review_ratings['dinner_cp'] = category_ratings[3]
                    review_ratings['dinner_drink'] = category_ratings[4]
                elif r.find('span', class_='c-rating__time c-rating__time--lunch') is not None:
                    # Lunch ratings
                    review_ratings['lunch_overall'] = float(r.find(
                        'b', class_='c-rating__val c-rating__val--strong').get_text(strip=True))
                    category_ratings = [np.nan if v.get_text(strip=True) == '-' else float(v.get_text(strip=True))
                                        for v in r.find_all('strong', class_='rvw-item__ratings-dtlscore-score')]
                    review_ratings['lunch_taste'] = category_ratings[0]
                    review_ratings['lunch_service'] = category_ratings[1]
                    review_ratings['lunch_mood'] = category_ratings[2]
                    review_ratings['lunch_cp'] = category_ratings[3]
                    review_ratings['lunch_drink'] = category_ratings[4]
                else:
                    print('Invalid review ratings !')

        # Review title
        tag_title = soup.find('p', class_='rvw-item__title')
        if tag_title is not None:
            review_title = tag_title.get_text(strip=True)
        else:
            review_title = 'unknown'

        # Review text
        tag_text = soup.find('div', class_='rvw-item__rvw-comment')
        if tag_text is not None:
            review_text = tag_text.find('p').get_text(strip=True)
        else:
            review_text = 'unknown'

        return TabelogReviews().input_retrieved_reviews(
            restaurant_name=restaurant_name, reviewer_url=reviewer_url, review_ratings=review_ratings,
            review_title=review_title, review_text=review_text)
    else:
        return TabelogReviews()


def get_review_pages(url, interval=1):
    url_review_page = url + 'dtlrvwlst/'

    review_pages = []
    while True:
        resp = requests.get(url_review_page)
        if resp.ok is True:
            soup = resp_to_soup(resp)

            review_pages += ['https://tabelog.com' + item['href'] for item
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

    return review_pages


def get_restaurant_pages(url, interval=1, display_progress=False):
    restaurant_pages = pd.DataFrame(columns=['Restaurant_name', 'Restaurant_url'])
    page = 1
    max_page = '?'
    restaurants_in_one_page = 20    # Can be obtained ?
    while True:
        resp = requests.get(url)
        if resp.ok is True:
            soup = resp_to_soup(resp)

            # Progress
            if page == 1:
                # Get max_page
                max_page = math.ceil(float(soup.find('div', class_='list-condition').find(
                    'span', class_='list-condition__count').get_text(strip=True)) / restaurants_in_one_page)
            if display_progress:
                print('Page: %s / %s' % (page, max_page))

            tags = soup.find_all('a', class_='list-rst__rst-name-target cpy-rst-name')
            restaurant_names = [tag.get_text(strip=True) for tag in tags]
            restaurant_urls = [tag['href'] for tag in tags]
            restaurant_pages = restaurant_pages.append(pd.DataFrame(
                {'Restaurant_name': restaurant_names, 'Restaurant_url': restaurant_urls}, index=np.arange(len(tags))),
                ignore_index=True)

            # Get next url
            if soup.find('a', class_='c-pagination__arrow c-pagination__arrow--next') is not None:
                url = soup.find('a', class_='c-pagination__arrow c-pagination__arrow--next')['href']
            else:
                break
        else:
            break

        # Sleep
        time.sleep(interval)
        page += 1

    return restaurant_pages
