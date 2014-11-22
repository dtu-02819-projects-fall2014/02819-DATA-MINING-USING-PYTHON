# -*- coding: utf-8 -*-

import functools
import configure_yelp_api
import data_layer.restaurant_scraper as place_scraper
import data_layer.user_scraper as user_scraper
import data_layer.mongo_handler as mongo_handler


def run(port=27017, host='localhost', with_drop=True):
    """
    Populates the specified mongodb

    Kwargs:
        port (str): Default mongodb port, change to use other port
        host (str): Change to your server
    """

    yelp_api = configure_yelp_api.config_api('conf.ini')
    scraper = user_scraper.UserScraper()
    handler = mongo_handler.YelpMongoHandler()

    if with_drop:
        handler.drop_collection('users_id')
        handler.drop_collection('places')
        handler.drop_collection('users_info')

    result_set = yelp_api.query_api('dinner', 'Copenhagen', 20)
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
