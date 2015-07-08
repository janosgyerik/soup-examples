#!/usr/bin/env python

from argparse import ArgumentParser
from urllib import request

from bs4 import BeautifulSoup


COM_URL_FORMAT = 'http://{}.com/election/{}?tab=primary'
STANDARD_URL_FORMAT = 'http://{}.stackexchange.com/election/{}?tab=primary'

SITES_INFO = [
    (('cr', 'codereview'), STANDARD_URL_FORMAT, 'codereview'),
    (('sf', 'serverfault'), COM_URL_FORMAT, 'serverfault'),
    (('so', 'stackoverflow'), COM_URL_FORMAT, 'stackoverflow'),
]

SITES = {}


def init_sites():
    for info in SITES_INFO:
        names, url_format, url_component = info
        for name in names:
            SITES[name] = url_format, url_component


init_sites()


def load_html_doc(url):
    return request.urlopen(url).read()


def get_soup(url):
    html_doc = load_html_doc(url)
    soup = BeautifulSoup(html_doc)
    # print(soup.prettify())
    return soup


def main():
    parser = ArgumentParser(description='Show candidates of an SE election in sorted order')
    parser.add_argument('site', choices=SITES.keys(),
                        help='Site short name or abbreviation')
    parser.add_argument('-n', type=int, default=1,
                        help='Election number')
    args = parser.parse_args()

    site_info = SITES[args.site]
    url_format, url_component = site_info
    url = url_format.format(url_component, args.n)

    soup = get_soup(url)
    scores = []
    for tr in soup.find_all('tr'):
        if tr.find('td', attrs={'class': 'votecell'}):
            username = tr.find(attrs={'class': 'user-details'}).find('a').text
            votes = int(tr.find(attrs={'class': 'vote-count-post'}).text)
            scores.append((username, votes))

    for name, score in sorted(scores, key=lambda x: x[1], reverse=True):
        print('{}\t{}'.format(score, name))


if __name__ == '__main__':
    main()
