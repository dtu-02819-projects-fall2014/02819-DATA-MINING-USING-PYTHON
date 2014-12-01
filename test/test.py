# -*- coding: utf-8 -*-

from os import (path, sys)
parentdir = path.dirname(path.dirname(path.abspath(__file__)))
sys.path.insert(0, parentdir)
from nose.tools import assert_equals
import urllib2
from bs4 import BeautifulSoup
from data_layer.user_scraper import UserScraper
import data_layer.restaurant_scraper as restaurant_scraper

# initial setup for testing the UserScraper

# use a downloaded html pages to test on
url_path_page = path.abspath('yelp_test_page.html')
url_path_user = path.abspath('yelp_profile_test_page.html')
url_path_empty = path.abspath('yelp_empty_user_test.html')
url_path_no_tag = path.abspath('yelp_user_no_price_cat_tag.html')
url_path_no_price = path.abspath('yelp_no_price_tag.html')
url_path_place = path.abspath('yelp_place_test_page.html')
test_url_page = 'file://{}'.format(url_path_page)
test_url_user = 'file://{}'.format(url_path_user)
test_url_empty = 'file://{}'.format(url_path_empty)
test_url_no_tag = 'file://{}'.format(url_path_no_tag)
test_url_no_price = 'file://{}'.format(url_path_no_price)
test_url_place = 'file://{}'.format(url_path_place)
local_test_url_page = urllib2.urlopen(test_url_page).read()
local_test_url_user = urllib2.urlopen(test_url_user).read()
local_test_url_empty = urllib2.urlopen(test_url_empty).read()
local_test_url_no_tag = urllib2.urlopen(test_url_no_tag).read()
local_test_url_no_price = urllib2.urlopen(test_url_no_price).read()
local_test_url_place = urllib2.urlopen(test_url_place).read()

test_soup_page = BeautifulSoup(local_test_url_page)
test_soup_user = BeautifulSoup(local_test_url_user)
test_soup_empty = BeautifulSoup(local_test_url_empty)
test_soup_no_tag = BeautifulSoup(local_test_url_no_tag)
test_soup_no_price = BeautifulSoup(local_test_url_no_price)
test_soup_place = BeautifulSoup(local_test_url_place)
scraper = UserScraper()
pages_user1 = [test_soup_user]
pages_user2 = [test_soup_empty]
scraper.soups = {'test_user': pages_user1, 'empty_user': pages_user2}

# Start testing


def test_replace_all():
    test_str = "<br>a\nb<address>c\nd<br>"
    replace_dict = {'\n': '', '<br>': '', '<address>': ''}
    assert_equals(scraper.replace_all(test_str, replace_dict), 'abcd')


def test_generate_review_url():
    test_str = u'http://www.yelp.com/user_details_reviews_self?'\
        u'userid=xW6wTwFRqtM5cV_tJTXrHA&review_filter=location&'\
        u'location_filter_city=K\xf8benhavn&location_filter_state'\
        u'=84&rec_pagestart=10'
    assert_equals(
        scraper.generate_review_url(
            'xW6wTwFRqtM5cV_tJTXrHA', 10, u'København', '84'), test_str)


def test_extract_address():
    assert_equals(scraper.extract_address(test_soup_page),
                  {'address': u'Esplanaden 4'})


def test_extract_address_empty():
    assert_equals(scraper.extract_address(test_soup_empty), {'address': ''})


def test_extract_information():
    assert_equals(scraper.extract_information(test_soup_page),
                  {'url': u'http://www.yelp.dk'
                   u'http://www.yelp.dk/biz/toldbod-bodega-k%C3%B8benhavn',
                   '_id': u'cqXYMV1alfHWKsgPBkreLQ',
                   'name': u'Toldbod Bodega'})


def test_extract_price_and_category_base_case():
    assert_equals(scraper.extract_price_and_category(test_soup_page),
                  {'price': 2,
                   'categories': [u'Bodegaer', u'Dansk', u'Smørrebrød']})


def test_extract_price_and_category_no_tags():
    assert_equals(scraper.extract_price_and_category(test_soup_no_tag),
                  {'price': None, 'categories': None})


def test_extract_price_and_category_no_price():
    assert_equals(scraper.extract_price_and_category(test_soup_no_price),
                  {'price': None,
                  'categories': [u'Ice Cream & Frozen Yogurt']})


def test_extract_price_and_category_empty():
    assert_equals(scraper.extract_price_and_category(test_soup_empty),
                  {'price': None,
                   'categories': None})


def test_extract_rating():
    assert_equals(scraper.extract_rating(test_soup_page),
                  {'created_at': u'19-11-2014',
                   'rating': 3.0, 'text': u'Et fors\xf8g p\xe5 at pr\xf8ve '
                   u'alle sm\xf8rrebr\xf8dsrestauranter i K\xf8benhavn .. (Du'
                   u' kan l\xe6se de andre her p\xe5 siden'})


def test_get_number_of_pages():
    assert_equals(scraper.get_number_of_pages(test_soup_page), 5)


def test_extract_user_information():
    assert_equals(scraper.extract_user_information('test_user'),
                  {'created_at': u'March 2014',
                   'location': u'N\xf8rrebro, K\xf8benhavn, Denmark',
                   'name': u'Stephanie "Princess" P.'})


def test_extract_votes():
    assert_equals(scraper.extract_votes('test_user'),
                  {'funny': 44,
                   'usefull': 283,
                   'cool': 141})


def test_extract_no_votes():
    assert_equals(scraper.extract_votes('empty_user'),
                  {'funny': None,
                   'usefull': None,
                   'cool': None})


def test_get_number_of_pages_place():
    assert_equals(restaurant_scraper.get_number_of_pages(test_soup_place), 2)


def test_next():
    assert_equals(restaurant_scraper.next('http://www.test.com', 2, 10),
                  'http://www.test.com?start=20')
