#-*- coding: utf-8 -*-

import ConfigParser
import data_layer.yelp_json as yelp_api
import data_layer.restaurant_scraper as place_scraper
import data_layer.user_scraper as user_scraper


def config_api(config_file):
    """

    """
    config = ConfigParser.ConfigParser()
    config.read(config_file)
    options = config.options('Tokens')
    conf_dict = {}

    for option in options:
        conf_dict[option] = config.get('Tokens', option)

    yelp_api_obj = yelp_api.YelpApiDataExtractor(
        conf_dict['consumer_key'],
        conf_dict['consumer_secret'],
        conf_dict['token'],
        conf_dict['token_secret'])

    return yelp_api_obj


def run():
    yelp_api = config_api('conf.ini')
    result_set = yelp_api.query_api('dinner', 'Copenhagen', 1)
    url_search_list = [url['url'] for url in result_set]
    users = place_scraper.scrap_users(url_search_list)
    users = [i for i, j in users.items()]
    scraper = user_scraper.UserScraper()
    scraper.scrap_users(u'københavn', users)

    return [scraper.places, scraper.users]
