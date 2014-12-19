#!/usr/bin/env python

from urllib import request

from bs4 import BeautifulSoup
import os


URL = 'http://winterbash2014.stackexchange.com/'


def load_html_doc(url):
    cached_file = 'cache/page.html'
    if os.path.isfile(cached_file) and os.path.getsize(cached_file):
        with open(cached_file) as fh:
            html_doc = fh.read()
    else:
        html_doc = request.urlopen(url).read()
        with open(cached_file, 'wb') as fh:
            fh.write(html_doc)
    return html_doc


def get_soup(url):
    html_doc = load_html_doc(url)
    return BeautifulSoup(html_doc)


def print_hats_as_gfm_checkboxes(soup):
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
