# -*- coding: utf-8 -*-

import urllib2
from bs4 import BeautifulSoup

url = "http://www.yelp.com/biz/upstate-new-york-2"

content = urllib2.urlopen(url).read()

soup = BeautifulSoup(content)


def scrap_users():
    """

    """

    for user in soup.find_all('a', class_='user-display-name'):
        user_hash = user.get('href').split('=')[1]
        user_name = user.get_text('data-hovercard-id')
        print u"{0} {1}".format(user_hash, user_name)


def next(base_url, next):
    """

    """

    return ''.join([base_url, '?start=', str(next)])
