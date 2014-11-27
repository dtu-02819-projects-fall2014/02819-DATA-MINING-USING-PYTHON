# -*- coding: utf-8 -*-

from nose.tools import assert_equals
import os
import urllib2
from bs4 import BeautifulSoup
from data_layer.user_scraper import UserScraper

# initial setup for testing the UserScraper

# use a downloaded html page to test on
url_path = os.path.abspath('test_data/yelp_user_test_page.html')
test_url = 'file://{}'.format(url_path)
local_test_url = urllib2.urlopen(test_url).read()

user_test_soup = BeautifulSoup(local_test_url)
scraper = UserScraper()

# tests


def test_replace_all():
    test_str = "<br>a\nb<address>c\nd<br>"
    replace_dict = {'\n': '', '<br>': '', '<address>': ''}
    assert_equals(scraper.replace_all(test_str, replace_dict), 'abcd')


def test_extract_address():
    assert_equals(scraper.extract_address(user_test_soup),
                  {'address': u'Esplanaden 4'})


def test_extract_information():
    assert_equals(scraper.extract_information(user_test_soup),
                  {'url': u'http://www.yelp.dk'
                   u'http://www.yelp.dk/biz/toldbod-bodega-k%C3%B8benhavn',
                   '_id': u'cqXYMV1alfHWKsgPBkreLQ',
                   'name': u'Toldbod Bodega'})


def test_extract_price_and_category_base_case():
    assert_equals(scraper.extract_price_and_category(user_test_soup),
                  {'price': 2,
                   'categories': [u'Bodegaer', u'Dansk', u'Smørrebrød']})


def test_extract_rating():
    assert_equals(scraper.extract_rating(user_test_soup),
                  {'created_at': u'19-11-2014',
                   'rating': 3.0, 'text': u'Et fors\xf8g p\xe5 at pr\xf8ve '
                   u'alle sm\xf8rrebr\xf8dsrestauranter i K\xf8benhavn .. (Du'
                   u' kan l\xe6se de andre her p\xe5 siden'})


def test_get_number_of_pages():
    assert_equals(scraper.get_number_of_pages(user_test_soup), 5)
