#!/usr/bin/env python

from urllib import request

from bs4 import BeautifulSoup
import os


URL = 'http://codereview.stackexchange.com/election/1?tab=primary'


def load_html_doc(url):
    return request.urlopen(url).read()
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
    # print_hats_as_gfm_checkboxes(soup)
    scores = []
    for tr in soup.find_all('tr'):
        if tr.find('td', attrs={'class': 'votecell'}):
            username = tr.find(attrs={'class': 'user-details'}).find('a').text
            votes = int(tr.find(attrs={'class': 'vote-count-post'}).text)
            scores.append((username, votes))

    for pair in sorted(scores, key=lambda x: x[1], reverse=True):
        print('{}\t{}'.format(pair[1], pair[0]))


if __name__ == '__main__':
    main()
