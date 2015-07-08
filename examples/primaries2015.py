#!/usr/bin/env python

from argparse import ArgumentParser
from urllib import request

from bs4 import BeautifulSoup


URL = 'http://codereview.stackexchange.com/election/1?tab=primary'
URL = 'http://serverfault.com/election/4?tab=primary'
URL_FORMAT = 'http://{}/election/{}?tab=primary'


def load_html_doc(url):
    return request.urlopen(url).read()


def get_soup(url):
    html_doc = load_html_doc(url)
    soup = BeautifulSoup(html_doc)
    # print(soup.prettify())
    return soup


def main():
    parser = ArgumentParser('asd')
    args = parser.parse_args()

    soup = get_soup(URL)
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
