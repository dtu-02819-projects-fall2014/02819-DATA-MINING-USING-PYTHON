# -*- coding: utf-8 -*-
import urllib2
from bs4 import BeautifulSoup
import re
from time import sleep
from random import uniform

from pymongo import MongoClient

client = MongoClient('localhost', 27017)
db = client.yelp_db
users_info = db.user_info
places = db.places

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


def get_user(user_id, length=100, city=u'k\xf8benhavn'):

    if users_info.find({'_id': user_id}).count() is not 0:
        print "user already in db"
        return

    # Getting the reviews

    page_start = 0
    reviews = []
    t_review_count = 0
    c_review_count = 0
    print 'getting reviews..'
    while True:
        print 'scrapping reviews from page %d' % (page_start / 10)
        soup = soup_reviews(user_id, page_start)

        for a in soup.find_all('div', class_='review clearfix'):
            r = {}
            p = {}
            t_review_count += 1

            rep = {'\n': ' ', 'St': 'St ', 'Ave': 'Ave ',
                   'Broadway': 'Broadway ', 'Blvd': 'Blvd ', 'Rd': 'Rd '}

            p['address'] = replace_all(a.find('address', class_='smaller')
                                       .get_text().strip(), rep)

            # we only want review from the city!!!!!!!
            if city in p['address'].lower():
                c_review_count += 1

                # We store the place in a separate database
                p['name'] = a.find('a').get_text().replace('\n', '').strip()
                p['_id'] = a.find(
                    'a').get('href').split('=')[1].replace('\n', '')

                p['price'] = None
                p['categories'] = [c.get_text('href').replace('\n', '').strip(
                ) for c in a.find('p').find_all('a')]

                # We only take the id and the name of the place in the review
                # in order to not overload the user
                r['place_id'] = p['_id']
                r['place_name'] = p['name']

                r['rating'] = float(a.find(
                    'div', class_='rating').find('i').get('title')[:3].strip())
                r['created_at'] = a.find(
                    class_='smaller date').get_text().replace('\n', '').strip()
                r['text'] = a.find(
                    'div', class_='review_comment').get_text().strip().replace(
                        '\n', '')
                if len(r['text']) > length:
                    r['text'] = r['text'][:length] + '...'
                reviews.append(r)
                if(places.find({'_id':p['_id']}).count() == 0):
                    places.insert(p)
                    print p['name'], 'inserted in places db'

        if len(soup.find_all('td',class_='nav-links')) <2:
            print 'getting user informations..'
    user = {}
    user['_id'] = user_id

    user['city_reviews_count'] = c_review_count
    user['total_reviews_count'] = t_review_count
    user['reviews'] = reviews

    rep = {'\n': '', ' \'s Profile': ''}

    # user name could also be retrived by the other db
    user['name'] = replace_all(
        soup.find('div', class_='about-connections').find(
            'h1').get_text(), rep).strip()

    s = soup.find('div', id='about_user_column')

    user['location'] = s.find(
        'div', id='profile_questions').find_all(
            'p')[0].get_text().replace('\n', '').strip()
    user['created_at'] = s.find(
        'div', id='profile_questions').find_all(
            'p')[1].get_text().replace('\n', '').strip()

    review_votes = s.find(
        'p', class_='i-review-votes-user_social-wrap').get_text()

    if review_votes is not None:
        rv = {}
        digits = map(int, re.findall('\d+', review_votes))
        rv['useful'], rv['funny'], rv['cool'] = digits[:3]
        rv['total'] = sum(digits)
    else:
        rv['useful'], rv['funny'], rv['cool'], rv['total'] = 0
    user['review_votes'] = rv

    users_info.insert(user)
    print user['name'], 'inserted in users_info db'

    return user


def replace_all(text, dic):
    for i, j in dic.iteritems():
        text = text.replace(i, j)
    return text
