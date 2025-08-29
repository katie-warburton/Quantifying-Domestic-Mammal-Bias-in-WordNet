'''
Functions used to scrape Wikipedia page IDs from lists of mammal species.
    - get_wiki_ids1 is used for pages that store mammal species in html list structure
    - get_wiki_ids2 is used for pages that store the mammal species in html table structure
'''

import requests
import re
from bs4 import BeautifulSoup

'''
Helper function for get_wiki_ids1. Gets all links from a page with an 
html list structure. 
'''
def scrape_wikipedia_links1(url):
    # Send a GET request to the Wikipedia page
    response = requests.get(url)
    wiki_links = []

    # Check if the request was successful (status code 200)
    if response.status_code == 200:
        # Parse the HTML content of the page
        soup = BeautifulSoup(response.text, 'html.parser')

        # Find all links in the page
        links = soup.find_all('a', href=re.compile(r'^/wiki/'))
        # Extract and print the links
        for link in links:
            list_item = link.find_parent('li')
            
            if list_item:
                # Extract and print the text next to the link within the list item
                text_next_to_link = list_item.get_text(separator=' ', strip=True)
                wiki_links.append((text_next_to_link.lower(), link['href']))
    return wiki_links

'''
Function to get Wikipedia page IDs for mammal species from a Wikipedia page where mammal
species wikipedia page links are stored in an html list structure. Pages must be manually 
inspected to find start (the first mammal list entry that should be parsed) and end 
(the last mammal list entry that should be parsed).

For example, on the page https://en.wikipedia.org/wiki/List_of_rodents:
    start = Ctenodactylus gundi - North African gundi
    end = Zyzomys woodwardi - Kimberley rock rat
'''
def get_wiki_ids1(url, start, end):
    wiki_links = scrape_wikipedia_links1(url)
    start_idx = next(i for i, t in enumerate(wiki_links) if t[0] == start.lower())
    end_idx = next(i for i, t in enumerate(wiki_links) if t[0] == end.lower())
    wiki_links = wiki_links[start_idx:end_idx+1]
    wiki_links = [link for link in wiki_links if 'genus ' not in link[0] and 
                  'family ' not in link[0] and 'order ' not in link[0] and 
                  'clade ' not in link[0] and 'tribe ' not in link[0] and 
                  'extinct' not in link[0] and '†' not in link[0]]
    uniq_links = {link[0]: link[1] for link in wiki_links}
    return list(set([link.replace('/wiki/', '').replace('#Taxonomy', '') for link in uniq_links.values()]))

'''
Function to get Wikipedia page IDs from a Wikipedia page where mammal species Wikipedia page links
are stored in an html table structure. Pages must be manually inspected to get the column that species
page IDs can be found in. 

For example on page: https://en.wikipedia.org/wiki/List_of_carnivorans and https://en.wikipedia.org/wiki/List_of_artiodactyls,
column_idx=0
'''
def get_wiki_ids2(url, column_idx):
    response = requests.get(url)
    wiki_links = []
    # Check if the request was successful (status code 200)
    if response.status_code == 200:
        # Parse the HTML content of the page
        soup = BeautifulSoup(response.text, 'html.parser')

        # Find the table based on its class
        tables = soup.find_all('table', {'class': 'wikitable'})
        for table in tables:
            rows = table.find_all('tr')

            # Extract and print the links from the specified column
            for row in rows:
                # Find all cells in the row
                cells = row.find_all('td')

                # Check if the column index is within the range of cells
                if 0 <= column_idx < len(cells):
                    # Find all links within the specified column
                    column_links = cells[column_idx].find_all('a', href=re.compile(r'^/wiki/'))
                    for link in column_links:
                        list_item = link.find_parent('li')
            
                        if list_item and '†' not in list_item.get_text(separator=' ', strip=True):
                            # Extract the text next to the link within the list item
                            wiki_links.append(link['href'])
    return list(set([link.replace('/wiki/', '').replace('#Taxonomy', '') for link in wiki_links]))