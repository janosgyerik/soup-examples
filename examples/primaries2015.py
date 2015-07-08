#!/usr/bin/env python

from argparse import ArgumentParser
from urllib import request

from bs4 import BeautifulSoup


STANDARD_URL_FORMAT = 'http://{}.stackexchange.com/election/{}?tab=primary'
COM_URL_FORMAT = 'http://{}.com/election/{}?tab=primary'

SITES_INFO_HELPER = [
    (('cr', 'codereview'), STANDARD_URL_FORMAT, 'codereview'),
    (('sf', 'serverfault'), COM_URL_FORMAT, 'serverfault'),
    (('so', 'stackoverflow'), COM_URL_FORMAT, 'stackoverflow'),
]


def build_sites_info():
    sites_info = {}
    for info in SITES_INFO_HELPER:
        names, url_format, url_component = info
        for name in names:
            sites_info[name] = url_format, url_component
    return sites_info


def load_html_doc(url):
    return request.urlopen(url).read()


def get_soup(url):
    html_doc = load_html_doc(url)
    soup = BeautifulSoup(html_doc)
    # print(soup.prettify())  # for debugging
    return soup


def main():
    sites_info = build_sites_info()

    parser = ArgumentParser(description='Show candidates of an SE election in sorted order')
    parser.add_argument('site', choices=sites_info.keys(),
                        help='Site short name or abbreviation')
    parser.add_argument('-n', type=int, default=1,
                        help='Election number')
    args = parser.parse_args()

    site_info = sites_info[args.site]
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
