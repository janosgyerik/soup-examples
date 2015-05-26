#!/usr/bin/env python

from urllib import request
from argparse import ArgumentParser
from datetime import date

from bs4 import BeautifulSoup
import os
import re

# todo
# option to load next weekday, for example sat, sun
# option to configure station
# cache control

URL_TEMPLATE = 'http://www.transdev-idf.com/horaire-arret-r1-GEECUA?j={}'


def load_html_doc(url, use_cache=False):
    cached_file = 'cache/page.html'
    if use_cache and os.path.isfile(cached_file) and os.path.getsize(cached_file):
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


def print_pretty(soup):
    print(soup.prettify())


def print_timetable(soup):
    for table in soup.find_all('table', attrs={'class': 'horaires'}):
        for td in table.find_all('td'):
            if re.match(r'\d+', td.text):
                minute = td.text
                hour = re.search(r'(\d+)', td.attrs['headers'][0]).group(0)
                print('{}:{}'.format(hour, minute))


def main():
    parser = ArgumentParser(description='Download timetable')
    parser.add_argument('-d', '--date')
    args = parser.parse_args()

    if args.date:
        datestr = args.date
    else:
        datestr = date.strftime(date.today(), '%d-%m-%Y')

    url = URL_TEMPLATE.format(datestr)
    soup = get_soup(url)

    print_timetable(soup)


if __name__ == '__main__':
    main()
