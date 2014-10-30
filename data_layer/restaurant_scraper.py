# -*- coding: utf-8 -*-

"""

"""

from __future__ import print_function
import urllib2
from bs4 import BeautifulSoup


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
            user_hashes[user_hash] = user_name

    return user_hashes


def next(base_url, next_page, num):
    """

    """
    if next == 0:
        return base_url

    return ''.join([base_url, '?start=', str(next_page*num)])


def construct_mongotable(dictionary):
    """

    """

    mongo_table = []

    for key, value in dictionary.iteritems():
        mongo_table.append({'_id': key, 'user_name': value})

    return mongo_table
