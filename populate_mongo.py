# -*- coding: utf-8 -*-

"""
Usage:
    populate_mongo.py <term> <location> <search_limit> <city> <filter_state>
    populate_mongo.py <term> <location> <search_limit> <city> <filter_state> <num_of_scraps>
    populate_mongo.py <term> <location> <search_limit> <city> <filter_state> <num_of_scraps> <drop_db>
    populate_mongo.py <term> <location> <search_limit> <city> <filter_state> <num_of_scraps> <drop_db> <port>
    populate_mongo.py <term> <location> <search_limit> <city> <filter_state> <num_of_scraps> <drop_db> <port> <host>
"""

import functools
import configure_yelp_api
import data_layer.restaurant_scraper as place_scraper
import data_layer.user_scraper as user_scraper
import data_layer.mongo_handler as mongo_handler
from data_layer.yelp_json import YelpApiError
from pymongo.errors import ConnectionFailure
from docopt import docopt


def run(term, location, search_limit, city, filter_state, num_of_scraps=5,
        drop_db=True, port=27017, host='localhost'):
    """
    Populates the specified mongodb

    Args:
        term (str): Specify which term to lookup, for example dinner
        location (str): Specify the location for example Copenhagen
        search_limet (int): How many results to return
        city (str): Specify which city the place and reviews has to come
        from to be scrapped
        filter_state (str): The Yelp fiter state, e.g. København is
        '84', paris is '75', New York is 'NY'

    Kwargs:
        num_of_scraps (int): Default 5, defines the number of user that is being
        scraped at a time.
        drop_db (bool): Default true, will drop db collections
        port (int): Default mongodb port, change to use other port
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

    # This fixes the memory issues with the amazon server, by splitting the
    # users up in sub lists
    partitioned_userList = list(partition(userList, num_of_scraps))

    for inner_list in partitioned_userList:
        scraper = user_scraper.UserScraper()
        scraper.scrap_users(city, filter_state, inner_list)
        map(functools.partial(
            handler.add_document, collection='places'), scraper.places)
        map(functools.partial(
            handler.add_document, collection='users_info'), scraper.users)


def partition(l, n):
    """
    Will create a generator that can be used to partition a list in a list of
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


def to_bool(s):
    """
    Converts the string 'true' to the bool type True and the string 'false'
    to False. This is done with both upper and lower case strings.

    Args:
        s (str): The string to convert

    Return:
        The bool evaluation of the string, of type bool
    """

    return s.lower() == 'true'

if __name__ == '__main__':
    try:
        args = docopt(__doc__, version='populate_mongo 1.0')
        term = args['<term>']
        location = args['<location>']
        search_limit = int(args['<search_limit>'])
        city = unicode(args['<city>'], 'utf-8')
        filter_state = args['<filter_state>']

        if args['<host>'] is not None:
            run(term, location, search_limit, city, filter_state,
                int(args['<num_of_scraps>']), to_bool(args['<drop_db>']),
                int(args['<port>']), args['<host>'])
        elif args['<port>'] is not None:
            run(term, location, search_limit, city, filter_state,
                int(args['<num_of_scraps>']), to_bool(args['<drop_db>']),
                int(args['<port>']))
        elif args['<drop_db>'] is not None:
            run(term, location, search_limit, city, filter_state,
                int(args['<num_of_scraps>']), to_bool(args['<drop_db>']))
        elif args['<num_of_scraps>'] is not None:
            run(term, location, search_limit, city, filter_state,
                int(args['<num_of_scraps>']))
        else:
            run(term, location, search_limit, city, filter_state)

    except YelpApiError as e:
        print e
    except ConnectionFailure as e1:
        print '{} check MongoDB connection'.format(e1)
    except Exception as e2:
        print e2
