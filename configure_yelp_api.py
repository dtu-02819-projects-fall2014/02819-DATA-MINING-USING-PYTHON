import ConfigParser
import data_layer.yelp_json as yelp_api


def config_api(config_file):
        """
        Config Yelp Api with token specified in the conf.ini file

        The file raises a YelpApiExceptions if the conf.ini file is not
        setup proberly.

        Args:
            confil_file (str): path of config.ini

        Return:
            A configured yelp api object
        """
        config = ConfigParser.ConfigParser()
        config.read(config_file)

        try:
            options = config.options('Tokens')

            conf_dict = {}

            for option in options:
                conf_dict[option] = config.get('Tokens', option)

        except ConfigParser.NoSectionError as e:
            raise yelp_api.YelpApiError('{} - invalid conf.ini file'.format(e))
        except ConfigParser.NoOptionError as e:
            raise yelp_api.YelpApiError('{} - invalid conf.ini file'.format(e))

        yelp_api_obj = yelp_api.YelpApiDataExtractor(
            conf_dict['consumer_key'],
            conf_dict['consumer_secret'],
            conf_dict['token'],
            conf_dict['token_secret'])

        return yelp_api_obj
