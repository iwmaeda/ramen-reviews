# Create a ramen shop list in Tokyo from the results log page of the eating log

# Import functions in libs
import os
import sys

sys.path.append(os.path.abspath('../../..'))
from libs.tabelog import get_restaurant_pages

# Get restaurant names
restaurant_pages = get_restaurant_pages('https://tabelog.com/tokyo/rstLst/MC/', interval=5, display_progress=True)

# Output restaurant_pages
with open('../../../data/tabelog/ramen_restaurant_names_in_Tokyo.txt', 'w', encoding='utf-8') as f:
    restaurant_pages.to_csv(f, index=False, encoding='utf-8')
