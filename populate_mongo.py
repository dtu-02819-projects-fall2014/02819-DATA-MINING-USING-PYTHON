# -*- coding: utf-8 -*-

import functools
import sys
import configure_yelp_api
import data_layer.restaurant_scraper as place_scraper
import data_layer.user_scraper as user_scraper
import data_layer.mongo_handler as mongo_handler


def run(term, location, search_limit, city, filter_state, drop_db=True,
        port=27017, host='localhost', num_of_scraps=5):
    """
    Populates the specified mongodb

    Args:
        term (str): Specify which term to lookup, for example dinner
        location (str): Specify the location for example Copenhagen
        search_limet (int): How many results to return
        city (str): Specify which city the place and reviews has to come
        from to be scrapped
        filter_state (str): The Yelp fiter state, e.g. København is
        '84', paris is '75', New York is 'NY

    Kwargs:
        drop_db (bool): Default true, will drop db collections
        port (str): Default mongodb port, change to use other port
        host (str): Change to your server
    """

    yelp_api = configure_yelp_api.config_api('conf.ini')
    handler = mongo_handler.YelpMongoHandler()

    if drop_db:
        handler.drop_collection('places')
        handler.drop_collection('users_info')

    result_set = yelp_api.query_api(term, location, search_limit)
    url_search_list = [url['url'] for url in result_set]

    users = place_scraper.scrap_users(url_search_list)
    userList = [user for user in users]

    len_u = len(userList)/num_of_scraps

    n = 0

    for i in xrange(len_u):
        n = i*num_of_scraps
        scraper = user_scraper.UserScraper()
        scraper.scrap_users(city, filter_state, userList[n:n+num_of_scraps])
        map(functools.partial(
            handler.add_document, collection='places'), scraper.places)
        map(functools.partial(
            handler.add_document, collection='users_info'), scraper.users)

    scraper = user_scraper.UserScraper()
    scraper.scrap_users(city, filter_state, userList[n+num_of_scraps:])

    map(functools.partial(
        handler.add_document, collection='places'), scraper.places)
    map(functools.partial(
        handler.add_document, collection='users_info'), scraper.users)


def partition(l, n):
    """
    Will yield a generator that can be used to partition a list in a list of
    lists with the same amount of elements in each inner list. In case of a
    partitionning that do not add up with the length of the list, the rest will
    be addes as the last elements in the outer list.

    Args:
        l (list): The list that should be partitioned
        n (int): The number of chunks to partitioning the list in

    yield:
        A generator use to partion
    """

    for i in xrange(0, len(l), n):
        yield l[i:i+n]

if __name__ == '__main__':
    try:
        term = sys.argv[1]
        location = sys.argv[2]
        search_limit = int(sys.argv[3])
        city = unicode(sys.argv[4], 'utf-8')
        filter_state = sys.argv[5]
        if len(sys.argv) > 6:
            drop_db = bool(sys.argv[6])
        elif len(sys.argv) > 7:
            port = int(sys.argv[7])
        elif len(sys.argv) > 8:
            host = sys.argv[8]

        if len(sys.argv) is 6:
            run(term, location, search_limit, city, filter_state)
        elif len(sys.argv) is 7:
            run(term, location, search_limit, city, filter_state, drop_db)
        elif len(sys.argv) is 8:
            run(term, location, search_limit, city,
                filter_state, drop_db, port)
        elif len(sys.argv) is 9:
            run(term, location, search_limit, city,
                filter_state, drop_db, port, host)

    except IndexError:
        print('Arguments should be: \n <term> <location> <search_limit> '
              '<city> <filter_state> <drop_db> (defualt: True) '
              '<port> (default: 27017) <host> (default: localhost)')
