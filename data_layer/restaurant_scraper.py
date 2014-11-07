# -*- coding: utf-8 -*-

"""

"""

import urllib2
from bs4 import BeautifulSoup
from pymongo import MongoClient

client = MongoClient('localhost', 27017)
db = client.yelp_db
users_id = db.users_id


def scrap_users(url):
    """

    """
    content = urllib2.urlopen(url).read()

    soup = BeautifulSoup(content)

    page_interval = int(soup.find('div', class_='page-of-pages'
                                  ).get_text().strip().split(' ')[-1])

    user_hashes = {}

    for page in xrange(page_interval):
        content = urllib2.urlopen(next(url, page, 40)).read()
        soup = BeautifulSoup(content)

        for user in soup.find_all('a', class_='user-display-name'):
            user_hash = user.get('href').split('=')[1]
            user_name = user.get_text('data-hovercard-id')

            if users_id.find({'_id': user_hash}).count() == 0:
                users_id.insert({'_id': user_hash, 'name': user_name})
                print ('\n', user_name, 'inserted in users_id db')
            else:
                print ('\n', user_name, 'already in users_id db')
            user_hashes[user_hash] = user_name

    return user_hashes


def next(base_url, next_page, num):
    """

    """
    if next == 0:
        return base_url

    return ''.join([base_url, '?start=', str(next_page*num)])
