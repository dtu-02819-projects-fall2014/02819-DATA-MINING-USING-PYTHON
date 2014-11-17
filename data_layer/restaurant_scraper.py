# -*- coding: utf-8 -*-

"""

"""

import urllib2
from bs4 import BeautifulSoup


def scrap_users(url_list):
    """
    :params url_list: list of yelp restaurant urls

    """
    user_hashes = {}

    for url in url_list:
        content = urllib2.urlopen(url).read()

        soup = BeautifulSoup(content)

        page_interval = get_number_of_pages(soup)

        for page in xrange(page_interval):
            content = urllib2.urlopen(next(url, page, 40)).read()
            soup = BeautifulSoup(content)

            for user in soup.find_all('a', class_='user-display-name'):
                user_hash = user.get('href').split('=')[1]
                user_name = user.get_text('data-hovercard-id')

                user_hashes[user_hash] = user_name

    return user_hashes


def get_number_of_pages(soup):
    """

    """
    number_of_pages = int(soup.find('div', class_='page-of-pages').get_text(
        ).strip().split(' ')[-1])

    return number_of_pages


def next(base_url, next_page, num):
    """

    """
    if next_page == 0:
        return base_url

    return ''.join([base_url, '?start=', str(next_page*num)])
