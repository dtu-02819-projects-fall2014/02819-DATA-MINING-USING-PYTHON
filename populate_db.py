#-*- coding: utf-8 -*-

import ConfigParser
import data_layer.yelp_json as yelp_api


def config_api(config_file):
    """
    Config Yelp Api with token specified in the conf.ini file

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
