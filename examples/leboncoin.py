#!/usr/bin/env python
from datetime import datetime
import textwrap
from urllib import request
from argparse import ArgumentParser

from bs4 import BeautifulSoup
import os
import pymongo
import re
from pymongo import MongoClient

CACHE_DIR = 'cache'
LABEL = 'leboncoin'
# URL_TEMPLATE = 'https://www.leboncoin.fr/voitures/offres/ile_de_france/?f=c&brd=Toyota&mdl=Yaris&fu=4&gb=2'
URL_TEMPLATE = 'https://www.leboncoin.fr/voitures/offres/ile_de_france/?f=c&brd=Toyota&mdl=Yaris&gb=2'

INCOMING_ITEMS_FILE = os.path.join(CACHE_DIR, 'incoming.txt')

LABEL_URL = 'url'
LABEL_TITLE = 'title'
LABEL_CITY = 'city'

LABEL_PRICE = 'price'
LABEL_YEAR = 'year'
LABEL_KM = 'km'

LABEL_CREATED_AT = 'created_at'
LABEL_CREATED_DAY = 'created_day'
LABEL_ARCHIVED_AT = 'archived_at'
LABEL_ARCHIVED_DAY = 'archived_day'

NAMES_DICT = {
    'Prix': LABEL_PRICE,
    'Année-modèle': LABEL_YEAR,
    'Kilométrage': LABEL_KM,
    'Ville': LABEL_CITY,
}


def load_html_doc(url, label, use_cache=False):
    if not os.path.isdir(CACHE_DIR):
        os.mkdir(CACHE_DIR)

    cache_file = os.path.join(CACHE_DIR, '{}-{}.html'.format(LABEL, label))
    if use_cache and os.path.isfile(cache_file) and os.path.getsize(cache_file):
        msg('using cache {}'.format(cache_file))
        with open(cache_file, encoding="ISO-8859-1") as fh:
            html_doc = fh.read()
    else:
        msg('fetching url {}'.format(url))
        html_doc = request.urlopen(url).read()

        msg('writing cache {}'.format(cache_file))
        with open(cache_file, 'wb') as fh:
            fh.write(html_doc)
    return html_doc


def get_soup(url, label, use_cache):
    html_doc = load_html_doc(url, label, use_cache)
    return BeautifulSoup(html_doc, 'html.parser')


def extract_value(item):
    return item.text.strip()


def extract_table(section):
    table = {}
    for line in section.find_all('div', attrs={'class': 'line'}):
        if line.find('h2'):
            prop = extract_value(line.find('span', attrs={'class': 'property'}))
            value = extract_value(line.find('span', attrs={'class': 'value'}))
            table[prop] = value
    return table


def clean_int(dirty_int):
    return int(re.sub(r'[^0-9]', '', dirty_int))


def refine_table(table):
    for orig, renamed in NAMES_DICT.items():
        if orig in table:
            table[renamed] = table[orig]

    if LABEL_PRICE in table:
        table[LABEL_PRICE] = clean_int(table[LABEL_PRICE])

    if LABEL_YEAR in table:
        table[LABEL_YEAR] = clean_int(table[LABEL_YEAR])

    if LABEL_KM in table:
        table[LABEL_KM] = clean_int(table[LABEL_KM])

    return table


def msg(text):
    print('*', text)


def today():
    return datetime.now().replace(hour=0, minute=0, second=0, microsecond=0)


def find_and_insert_new(soup, use_cache):
    db = get_db()

    incoming_urls = set()
    incoming_items = []

    content = soup.find('section', attrs={'class': 'tabsContent'})
    for i, li in enumerate(content.find_all('li')):
        a = li.find('a')
        url = 'https:' + a.get('href')
        incoming_urls.add(url)

        if db.cars.count({LABEL_URL: url}):
            continue

        title = a.get(LABEL_TITLE)

        soup = get_soup(url, 'result{}'.format(i), use_cache)
        section = soup.find('section')

        table = refine_table(extract_table(section))
        table[LABEL_URL] = url
        table[LABEL_TITLE] = title
        table[LABEL_CREATED_AT] = datetime.now()
        table[LABEL_CREATED_DAY] = today()

        result = db.cars.insert_one(table)

        msg('inserted {}, id = {}'.format(title, result.inserted_id))

        incoming_items.append(table)

    with open(INCOMING_ITEMS_FILE, 'w') as fh:
        for item in incoming_items:
            fh.write(to_string(item))
            fh.write('\n')

    return incoming_urls


def remove_old(incoming_urls):
    db = get_db()

    for item in db.cars.find():
        if item[LABEL_URL] not in incoming_urls:
            item[LABEL_ARCHIVED_AT] = datetime.now()
            item[LABEL_ARCHIVED_DAY] = today()
            msg('archiving {}, id = {}'.format(item[LABEL_TITLE], item['_id']))
            db.cars_archive.insert_one(item)

            msg('removing {}, id = {}'.format(item[LABEL_TITLE], item['_id']))
            db.cars.remove({LABEL_URL: item[LABEL_URL]})


def update(use_cache):
    url = URL_TEMPLATE.format()
    soup = get_soup(url, 'index', use_cache)

    incoming_urls = find_and_insert_new(soup, use_cache)
    remove_old(incoming_urls)


def to_string(item):
    return textwrap.dedent('''
    {title}
    {url}
    {price}, {year}, {km}, {city}
    '''.format(title=item[LABEL_TITLE], url=item[LABEL_URL], price=item[LABEL_PRICE],
               year=item[LABEL_YEAR], km=item[LABEL_KM], city=item[LABEL_CITY])).lstrip()


def print_item(item):
    print(to_string(item))


def print_items(cursor):
    cursor = cursor.sort([
        (LABEL_PRICE, pymongo.ASCENDING)
    ])
    for item in cursor:
        print_item(item)


def print_new():
    print_items(get_db().cars.find({LABEL_CREATED_DAY: today()}))


def print_archived():
    print_items(get_db().cars_archive.find({LABEL_ARCHIVED_DAY: today()}))


def any_added_today():
    return get_db().cars.count({LABEL_CREATED_DAY: today()}) > 0


def any_archived_today():
    return get_db().cars_archive.count({LABEL_ARCHIVED_DAY: today()}) > 0


def report():
    if any_added_today():
        print('Entries added today:')
        print()
        print_new()

    if any_archived_today():
        print('Entries archived today:')
        print()
        print_archived()


def get_db():
    return MongoClient().test


def main():
    parser = ArgumentParser(description='')
    parser.add_argument('command', choices=['update', 'report'])
    parser.add_argument('--use-cache', action='store_true')
    args = parser.parse_args()

    if args.command == 'update':
        update(args.use_cache)
    elif args.command == 'report':
        report()


if __name__ == '__main__':
    main()
