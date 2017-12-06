# Create a ramen shop list in Tokyo from the results log page of the eating log

# Import functions in libs
import os
import sys

import requests

from bs4 import BeautifulSoup


sys.path.append(os.path.abspath('../../..'))
from libs.tabelog import get_restaurant_pages

# Ramen restaurants in Tokyo
url_ramen_Tokyo = 'https://tabelog.com/tokyo/rstLst/MC/'

# Get areas in Tokyo
resp = requests.get(url_ramen_Tokyo)
if resp.ok is True:
    soup = BeautifulSoup(resp.text, 'lxml')
    



# Get restaurant names
restaurant_pages = get_restaurant_pages('https://tabelog.com/tokyo/rstLst/MC/', interval=5, display_progress=True)

# Output restaurant_pages
with open('../../../data/tabelog/ramen_restaurant_names_in_Tokyo.txt', 'w', encoding='utf-8') as f:
    restaurant_pages.to_csv(f, index=False, encoding='utf-8')
