# Create a ramen shop list in Tokyo from the results log page of the eating log

import os
import sys
import time

import numpy as np
import pandas as pd
import requests
from bs4 import BeautifulSoup

sys.path.append(os.path.abspath('../../..'))
from libs.tabelog import get_restaurant_pages

# Ramen restaurants in Tokyo
url_ramen_Tokyo = 'https://tabelog.com/tokyo/rstLst/MC/'

# Get cities in Tokyo
resp = requests.get(url_ramen_Tokyo)
soup = BeautifulSoup(resp.text, 'lxml')

tags = soup.find('div', id='tabs-panel-balloon-pref-city').find_all('a', class_='icon-b-arrow-orange')
city_names = [tag.get_text(strip=True) for tag in tags]
city_urls = [tag['href'] for tag in tags]
df_cities = pd.DataFrame({'City_name': city_names, 'City_url': city_urls}, index=np.arange(len(tags)))

# Get restaurant names for each city
txt_output = '../../../data/tabelog/ramen_restaurant_names_in_Tokyo.txt'
pd.DataFrame(columns=['City', 'Restaurant_name', 'Restaurant_url']).to_csv(
    txt_output, sep='\t', index=False, encoding='utf-8')
for _, row in df_cities.iterrows():
    print('City name: %s' % (row['City_name']))
    restaurant_pages = get_restaurant_pages(row['City_url'], interval=5, display_progress=True)

    if len(restaurant_pages) != 0:
        # Output restaurant_pages
        restaurant_pages['City'] = row['City_name']
        with open(txt_output, 'a', encoding='utf-8') as f:
            restaurant_pages.loc[:, ['City', 'Restaurant_name', 'Restaurant_url']].to_csv(
                f, sep='\t', header=False, index=False, encoding='utf-8')

    # Sleep
    time.sleep(5)
