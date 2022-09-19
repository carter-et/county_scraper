"""
This script creates a json of state counties, ordered in alphabetical state order
Stops after reading Wyoming
"""

from bs4 import BeautifulSoup as bs
import re
import json
import requests

# GLOBAL VARS
LINK = 'https://en.wikipedia.org/wiki/List_of_counties_by_U.S._state_and_territory'
LAST_STATE = 'Wyoming'

headers = requests.utils.default_headers()
headers.update(
    {
        'User-Agent': 'My User Agent 1.0',
    }
)

def clean_county_text(text, state_name):
    text = text.replace(', ' + state_name, '')
    text = re.sub(r'[\[+\d\]]', '', text)
    text.strip()

    return text

"""
Scrapes county data for every state
Returns:
    - A list of tuples: [(state_name, [list of county_names]), ...],
        (List and not dict because we want these in the order we read them.)
"""
def scrape(link=LINK):
    # get page html
    response = requests.get(link, headers=headers, timeout=10)
    html = bs(response.content, 'html.parser')

    states_and_counties = []

    state_name = ''
    for tag in html.find_all('h2')[1:]:
        if state_name == LAST_STATE :
            break

        state_name = tag.text.strip().replace('[edit]', '').replace(' (USA)', '')

        ol = tag.find_next('ol')
        
        counties = []
        for il in ol.children:
            county = clean_county_text(il.text, state_name)

            # Unique case for Alaska
            if county.find('Unorganized Borough') > -1:
                boroughs = county.split('\n')
                for borough in boroughs:
                    counties.append(borough)

            elif county != '\n':
                counties.append(county)

        states_and_counties.append({'state': state_name, 'counties': counties})

    print(json.dumps(states_and_counties))

if __name__ == '__main__':
    scrape()