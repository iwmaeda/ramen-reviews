# Create review list of ramen restaurants in Tokyo
# get_ramen_restaurant_names_in_Tokyo.py needs to be executed first

import os
import sys
import time

import pandas as pd
import requests

sys.path.append(os.path.abspath('../../..'))
from libs.tabelog import get_review_pages, get_review_text

# Ramen restaurant list in Tokyo
restaurant_pages = pd.read_csv('../../../data/tabelog/ramen_restaurant_names_in_Tokyo.txt', sep='\t')

txt_output = '../../../data/tabelog/ramen_reviews_in_Tokyo.txt'
columns = ['Restaurant_name', 'City', 'reviewer_url', 'review_title', 'review_text',
           'dinner_overall', 'dinner_taste', 'dinner_service', 'dinner_mood', 'dinner_cp', 'dinner_drink',
           'lunch_overall', 'lunch_taste', 'lunch_service', 'lunch_mood', 'lunch_cp', 'lunch_drink']
pd.DataFrame(columns=columns).to_csv(txt_output, sep='\t', index=False, encoding='utf-8')
for _, row in restaurant_pages.iterrows():
    print('Restaurant name: %s' % (row['Restaurant_name']))
    # Get urls of review pages
    review_pages = get_review_pages(row['Restaurant_url'], interval=2)
    # Sleep
    time.sleep(2)
    # Get reviews
    df_reviews = pd.DataFrame(columns=columns)
    for page in review_pages:
        resp = requests.get(page)
        tabelog_review = get_review_text(resp)

        if tabelog_review.ok is True:
            df_reviews = df_reviews.append(pd.DataFrame(
                data=tabelog_review.output_retrieved_reviews(), index=[0]), ignore_index=True)
        # Sleep
        time.sleep(2)

    # Output reviews
    df_reviews['Restaurant_name'] = row['Restaurant_name']
    df_reviews['City'] = row['City']
    with open(txt_output, 'a', encoding='utf-8') as f:
        df_reviews.loc[:, columns].to_csv(f, sep='\t', header=False, index=False, encoding='utf-8')
