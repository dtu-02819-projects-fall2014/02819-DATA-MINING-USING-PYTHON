# -*- coding: utf-8 -*-

"""
Script for scraping places on the yelp webside

"""

import urllib2
from bs4 import BeautifulSoup


def scrap_users(url_list):
    """
    Takes a list of place url and returns all the user id hashes
    that have writte a review of the place.

    Args:
        url_list (str): The url to the place

    Return:
        A dict object with all user id hashes and user names

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
    Returns the number of pages on a place site

    Args:
        soup (bs4.elements.tag):the soup object to find the number of pages in

    Return:
        int -- the number of pages
    """
    number_of_pages = int(soup.find('div', class_='page-of-pages').get_text(
        ).strip().split(' ')[-1])

    return number_of_pages


def next(base_url, next_page, num):
    """
    Given a url the the base place site, the first page, and the next page as
    a number it returns the url as a str to the next page with the correct
    page number

    Args:
        base_url (str): The url to the base page of the place
        next_page (int): The page number to go to
        num (int): The interval the page is partition in
    """
    if next_page == 0:
        return base_url

    return ''.join([base_url, '?start=', str(next_page*num)])
