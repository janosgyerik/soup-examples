#!/usr/bin/env python

from urllib import request

from bs4 import BeautifulSoup
import os


URL = 'http://winterbash2014.stackexchange.com/'

CACHE_DIR = os.path.join(os.path.dirname(__file__), '.cache')
CACHE_FILE = os.path.join(CACHE_DIR, 'page.html')


def load_html_doc(url):
    if os.path.isfile(CACHE_FILE) and os.path.getsize(CACHE_FILE):
        with open(CACHE_FILE) as fh:
            html_doc = fh.read()
    else:
        html_doc = request.urlopen(url).read()
        if not os.path.isdir(CACHE_DIR):
            os.mkdir(CACHE_DIR)
        with open(CACHE_FILE, 'wb') as fh:
            fh.write(html_doc)
    return html_doc


def get_soup(url):
    html_doc = load_html_doc(url)
    return BeautifulSoup(html_doc)


def print_hats_as_gfm_checkboxes(soup):
    # print(soup.find('a', attrs={'class': 'boxes'}).text)
    for box in soup.find_all('a', attrs={'class': 'box'}):
        name = box.find(attrs={'class': 'hat-name'}).text
        description = box.find(attrs={'class': 'hat-description'}).text
        print('- [ ] {}: {}'.format(name, description))


def print_pretty(soup):
    print(soup.prettify())


def main():
    soup = get_soup(URL)
    print_hats_as_gfm_checkboxes(soup)
    # print_pretty(soup)


if __name__ == '__main__':
    main()
