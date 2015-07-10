#!/usr/bin/env python

from argparse import ArgumentParser
from urllib import request

from bs4 import BeautifulSoup


STANDARD_URL_FORMAT = 'http://{}.stackexchange.com/election/{}?tab=primary'
COM_URL_FORMAT = 'http://{}.com/election/{}?tab=primary'


class SiteInfo:
    sites = {}

    def __init__(self, name, domain, *aliases):
        self.name = name
        self.domain = domain
        self.sites[name] = self
        for alias in aliases:
            self.sites[alias] = self

    def get_primary_url(self, num=1):
        return 'http://{}/election/{}?tab=primary'.format(self.domain, num)

    @staticmethod
    def by_name(name):
        return SiteInfo.sites[name]

    @staticmethod
    def get_site_names():
        return SiteInfo.sites.keys()

SiteInfo('codereview', 'codereview.stackexchange.com', 'cr')
SiteInfo('serverfault', 'serverfault.com', 'sf')
SiteInfo('stackoverflow', 'stackoverflow.com', 'so')


def load_html_doc(url):
    return request.urlopen(url).read()


def get_soup(url):
    html_doc = load_html_doc(url)
    soup = BeautifulSoup(html_doc, 'html.parser')
    # print(soup.prettify())  # for debugging
    return soup


def main():
    site_names = SiteInfo.get_site_names()

    parser = ArgumentParser(description='Show candidates of an SE election in sorted order')
    parser.add_argument('site', choices=site_names,
                        help='Site name or abbreviation')
    parser.add_argument('-n', '--num', type=int, default=1,
                        help='Election number')
    args = parser.parse_args()

    url = SiteInfo.by_name(args.site).get_primary_url(args.num)

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
