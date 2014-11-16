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


def put_it(user_id, city):
    """

    """
    places = []

    soup = soup_reviews(user_id, 0)

    page_interval = get_number_of_pages(soup)

    for page in xrange(page_interval):
        if page is not 0:
            soup = soup_reviews(user_id, page_interval*10)

        places.extend(scrap_users_places(soup, city))

    return places


def scrap_users_places(soup, city):
    """

    """
    places = []

    for review in soup.find_all('div', class_='review'):
        address = extract_address(review)
        if city in address['address']:
            id_name = extract_id_and_name(review)
            price_category = extract_price_and_category(review)

            merge_dicts = reduce(lambda d1, d2: dict(d1, **d2),
                                 (id_name,
                                  address,
                                  price_category))

            places.append(merge_dicts)

    return places


def scrap_users_places_2(user_id, city):
    """

    """
    places = []

    soup = soup_reviews(user_id, 0)

    page_interval = get_number_of_pages(soup)

    for page in xrange(page_interval):
        if page is not 0:
            soup = soup_reviews(user_id, page*10)

        for review in soup.find_all('div', class_='review'):
            address = extract_address(review)
            if city in address['address']:
                id_name = extract_id_and_name(review)
                price_category = extract_price_and_category(review)

                merge_dicts = reduce(lambda d1, d2: dict(d1, **d2),
                                     (id_name,
                                      address,
                                      price_category))

                places.append(merge_dicts)

    return places


def get_number_of_pages(soup_snippet):
    """

    """
    return int(soup_snippet.find(
        'td', class_='range-of-total').get_text().strip().split(' ')[-1])


def replace_all(text, dic):
    for i, j in dic.iteritems():
        text = text.replace(i, j)
    return text


def extract_address(soup_snippet):
    """
    bs4.element.Tag
    """
    soup_snippet_string = str(soup_snippet.find('address'))

    # Deals with all the first addr lines in address string,
    # last address line is a special case
    cleaned_addr_list = replace_all(soup_snippet_string,
                                    {'\n': '',
                                     '<br>': ',',
                                     '<address>': ''}
                                    ).strip().split(',')[:-1]

    return {'address': ' '.join(
        item.decode('utf-8') for item in cleaned_addr_list)}


def extract_id_and_name(soup_snippet):
    """

    """
    hash_value = soup_snippet.find(
        'a', class_="biz-name").get('data-hovercard-id')

    name = soup_snippet.find('a', class_='biz-name').get_text()

    return {'_id': hash_value, 'name': name}


def extract_price_and_category(soup_snippet):
    """

    """
    price_category_list = soup_snippet.find(
        'div', class_='price-category').get_text().split('\n')

    # clean up the list
    price_category_list = [i for i in price_category_list if i is not u'']
    category_index = 0 if len(price_category_list) is 1 else 1
    price_category_list[category_index] = [
        i.strip() for i in price_category_list[category_index].split(',')]

    # translate the yelp price symbol into a integer, if price exists
    if category_index > 0:
        price_category_list[0] = len(price_category_list[0])

        return {'price': price_category_list[0],
                'categories': price_category_list[category_index]}

    return {'categories': price_category_list[category_index]}


def extract_rating(soup_snippet, review_length=100):
    """

    """
    rating = float(soup_snippet.find('div', class_='rating-very-large').find(
        'i').get('title').split(' ')[0])

    rating_date = soup_snippet.find(
        'span', class_='rating-qualifier').get_text().strip()

    rating_text = soup_snippet.find(
        'div', class_='review-content').find('p').get_text()[:review_length]

    return {'rating': rating, 'created_at': rating_date, 'text': rating_text}
