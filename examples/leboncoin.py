#!/usr/bin/env python
from datetime import datetime
from urllib import request
from argparse import ArgumentParser

from bs4 import BeautifulSoup
import os
import pymongo
import re
from pymongo import MongoClient

CACHE_DIR = 'cache'
LABEL = 'leboncoin'
URL_TEMPLATE = 'https://www.leboncoin.fr/voitures/offres/ile_de_france/?f=c&brd=Toyota&mdl=Yaris&fu=4&gb=2'
# URL_TEMPLATE = 'https://www.leboncoin.fr/voitures/offres/ile_de_france/?f=c&brd=Toyota&mdl=Yaris&gb=2'

LABEL_PRICE = 'Prix'
LABEL_YEAR = 'Année-modèle'
LABEL_KM = 'Kilométrage'


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

    content = soup.find('section', attrs={'class': 'tabsContent'})
    for i, li in enumerate(content.find_all('li')):
        a = li.find('a')
        url = 'https:' + a.get('href')
        incoming_urls.add(url)

        if db.cars.count({'url': url}):
            continue

        title = a.get('title')

        soup = get_soup(url, 'result{}'.format(i), use_cache)
        section = soup.find('section')

        table = refine_table(extract_table(section))
        table['url'] = url
        table['title'] = title
        table['created_at'] = datetime.now()
        table['created_day'] = today()

        result = db.cars.insert_one(table)

        msg('inserted {}, id = {}'.format(title, result.inserted_id))

    return incoming_urls


def remove_old(incoming_urls):
    db = get_db()

    for item in db.cars.find():
        if item['url'] not in incoming_urls:
            item['archived_at'] = datetime.now()
            item['archived_day'] = today()
            msg('archiving {}, id = {}'.format(item['title'], item['_id']))
            db.cars_archive.insert_one(item)

            msg('removing {}, id = {}'.format(item['title'], item['_id']))
            db.cars.remove({'url': item['url']})


def update(use_cache):
    url = URL_TEMPLATE.format()
    soup = get_soup(url, 'index', use_cache)

    incoming_urls = find_and_insert_new(soup, use_cache)
    remove_old(incoming_urls)


def print_new():
    db = get_db()
    cursor = db.cars.find().sort([
        ("Prix", pymongo.ASCENDING)
    ])
    for item in cursor:
        print(item['title'])
        print(item['url'])
        print(item['Prix'], item['Année-modèle'], item['Kilométrage'], item['Ville'], sep=', ')
        print()


def get_db():
    return MongoClient().test


def main():
    parser = ArgumentParser(description='')
    parser.add_argument('command', choices=['update', 'print-new'])
    parser.add_argument('--use-cache', action='store_true')
    args = parser.parse_args()

    if args.command == 'update':
        update(args.use_cache)
    elif args.command == 'print-new':
        print_new()


if __name__ == '__main__':
    main()
