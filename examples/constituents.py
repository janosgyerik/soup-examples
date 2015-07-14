#!/usr/bin/env python

from argparse import ArgumentParser
from urllib import request

from bs4 import BeautifulSoup
import re


class SiteInfo:
    sites = {}

    def __init__(self, name, domain, *aliases):
        self.name = name
        self.domain = domain
        self.sites[name] = self
        for alias in aliases:
            self.sites[alias] = self

    def get_constituents_url(self, page=1):
        return 'http://{}/help/badges/85?page={}'.format(self.domain, page)

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


def print_users(site, page):
    url = SiteInfo.by_name(site).get_constituents_url(page)

    soup = get_soup(url)
    for user_details in soup.find_all('div', attrs={'class': 'user-details'}):
        link = user_details.find(href=re.compile("^/users/"))
        user_id = link['href'].split('/')[2]
        username = link.text
        print('{}\t{}'.format(user_id, username))


def main():
    site_names = SiteInfo.get_site_names()

    parser = ArgumentParser(description='Get list of users who have the Constituent badge')
    parser.add_argument('site', choices=site_names,
                        help='Site name or abbreviation')
    args = parser.parse_args()

    for page in range(1, 12):
        print_users(args.site, page)
        break


if __name__ == '__main__':
    main()
