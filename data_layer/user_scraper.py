# -*- coding: utf-8 -*-
import urllib2
from bs4 import BeautifulSoup
from time import sleep
from random import uniform


def soup_reviews(user_id, page_start):
    url = 'http://www.yelp.com/user_details_reviews_self?userid=%s'\
        '&rec_pagestart=%d' % (user_id, page_start)
    content = urllib2.urlopen(url).read()
    return BeautifulSoup(content)


def soup_friends(user_id):
    friends_url = 'http://www.yelp.com/user_details_friends?userid=%s'\
        % (user_id)
    content = urllib2.urlopen(friends_url).read()
    return BeautifulSoup(content)


def sleep_rand():
    a = uniform(0.1, 0.5)
    print "sleeping %.2f seconds" % (a)
    sleep(a)


def scrap_reviews(user_id, city, length=100):
    """

    """
    restaurants = []

    soup = soup_reviews(user_id, 0)

    page_interval = int(soup.find(
        'td', class_='range-of-total').get_text().strip().split(' ')[-1])/10

    for page in xrange(page_interval):
        if page is not 0:
            soup = soup_reviews(user_id, page*10)

        for review in soup.find_all('div', class_='review'):
            address = extract_restaurant_address(review)
            if 'K\xc3\xb8benhavn' in address[-1]:
                restaurants.append(address)

    return restaurants


def replace_all(text, dic):
    for i, j in dic.iteritems():
        text = text.replace(i, j)
    return text


def extract_restaurant_address(soup_snippet):
    """
    bs4.element.Tag
    """
    name = soup_snippet.find('a', class_='biz-name').get_text()

    soup_snippet_string = str(soup_snippet.find('address'))

    # Deals with all the first addr lines in address string,
    # last address line is a special case
    cleaned_addr_list = replace_all(soup_snippet_string,
                                    {'\n': '',
                                     '<br>': ',',
                                     '<address>': ''}
                                    ).strip().split(',')[:-1]

    return_address_list = [name]
    return_address_list.extend(cleaned_addr_list)

    return return_address_list
