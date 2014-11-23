# -*- coding: utf-8 -*-

import functools
import sys
import configure_yelp_api
import data_layer.restaurant_scraper as place_scraper
import data_layer.user_scraper as user_scraper
import data_layer.mongo_handler as mongo_handler


def run(term, location, search_limit, drop_db=True,
        port=27017, host='localhost'):
    """
    Populates the specified mongodb

    Args:
        term (str): Specify which term to lookup, for example dinner
        location (str): Specify the location for example Copenhagen
        search_limet (int): How many results to return

    Kwargs:
        drop_db (bool): Default true, will drop db collections
        port (str): Default mongodb port, change to use other port
        host (str): Change to your server
    """

    yelp_api = configure_yelp_api.config_api('conf.ini')
    scraper = user_scraper.UserScraper()
    handler = mongo_handler.YelpMongoHandler()

    if drop_db:
        handler.drop_collection('users_id')
        handler.drop_collection('places')
        handler.drop_collection('users_info')

    result_set = yelp_api.query_api(term, location, search_limit)
    url_search_list = [url['url'] for url in result_set]

    users = place_scraper.scrap_users(url_search_list)
    userList = [user for user in users]

    scraper.scrap_users(u'københavn', '84', userList)
    usersCollection = [{'_id': i, 'name': j} for i, j in users.items()]

    map(functools.partial(
        handler.add_document, collection='users_id'), usersCollection)
    map(functools.partial(
        handler.add_document, collection='places'), scraper.places)
    map(functools.partial(
        handler.add_document, collection='users_info'), scraper.users)

if __name__ == '__main__':
    try:
        term = sys.argv[1]
        location = sys.argv[2]
        search_limit = int(sys.argv[3])
        if len(sys.argv) > 4:
            drop_db = bool(sys.argv[4])
        elif len(sys.argv) > 5:
            port = int(sys.argv[5])
        elif len(sys.argv) > 6:
            host = sys.argv[6]

        if len(sys.argv) is 4:
            run(term, location, search_limit)
        elif len(sys.argv) is 5:
            run(term, location, search_limit, drop_db)
        elif len(sys.argv) is 6:
            run(term, location, search_limit, drop_db, port)
        elif len(sys.argv) is 7:
            run(term, location, search_limit, drop_db, port, host)

    except IndexError:
        print('Arguments should be: \n term, location, search_limit,'
              'drop_db (defualt: True), port (default: 27017),'
              'host (default: localhost)')
