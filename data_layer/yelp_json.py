# -*- coding: utf-8 -*-

import json
import urllib
import urllib2
import oauth2


class YelpApiDataExtractor:
    """
    This class is based on the script the yelp links to in its torurial.
    The YelpApiDataExtractor, is a rewrite of this script, inorder to make
    it simpler to interface with a more generel system. The original script can
    be found at https://github.com/Yelp/yelp-api/tree/master/v2/python

    The class is only considering businesses.

    To get the tokens, one have to sign up at yelp.

    Args:
        consumer_key (str): The token that yelp provides
        consumer_secret (str): The token that yelp provides
        token (str): The token that yelp provides
        token_secret (str): The token that yelp provides.
    """

    API_HOST = 'api.yelp.com'
    SEARCH_PATH = '/v2/search/'

    def __init__(self, consumer_key, consumer_secret, token, token_secret):
        self.consumer_key = consumer_key
        self.consumer_secret = consumer_secret
        self.token = token
        self.token_secret = token_secret

    def query_api(self, term, location, search_limit):
        """
        Call thisscraper.extract_information() methos inorder to query the api

        Args:
            term (str): The term could be 'dinner' e.g. it should correspond
            to yelp term.
            location (str): This is location that is registered in the api,
            this means that is should be speled in english, so Copenhagen, not
            København.
            search_limit (int): How many results should be returned, their is
            an unknown upper limit, a exception will be thrown if that limit
            is reach

            Return:
                The result set in json format
        """
        try:
            response = self.__search(term, location, search_limit)
        except YelpApiError as e:
            print e
            return

        businesses = response.get('businesses')

        return businesses

    def __search(self, term, location, search_limit):
        """
        The methods handles the search parameters, and wraps inside a url that
        can be passed to API.

        Return:
            The request to the API

        """

        url_params = {
            'term': term,
            'location': location,
            'limit': search_limit
        }

        return self.__request(self.API_HOST, self.SEARCH_PATH,
                              url_params=url_params)

    def __request(self, host, path, url_params=None):
        """
        Handles the specific url to API, and is turning the API response into
        json. The method throw exception if it is not possible to make a
        connection to the yelp API, or if it not possible to load the json.

        Return:
            A json response from the yelp API

        """
        url_params = url_params or {}
        encoded_params = urllib.urlencode(url_params)

        url = 'http://{0}{1}?{2}'.format(host, path, encoded_params)

        signed_url = self.__oatuh(url)

        connection = None

        try:
            connection = urllib2.urlopen(signed_url, None)
            response = json.loads(connection.read())
        except urllib2.HTTPError as e:
            raise YelpApiError('{0} --> Check parameters'.format(e))
        except ValueError as e1:
            raise YelpApiError(e1)
        finally:
            if connection is not None:
                connection.close()

        return response

    def __oatuh(self, url):
        """
        Puth the oatuh2 token in the url

        Return:
            A signed url, that can be passed to the yelp API

        """
        consumer = oauth2.Consumer(self.consumer_key, self.consumer_secret)

        oauth_request = oauth2.Request('GET', url, {})
        oauth_request.update(
            {
                'oauth_nonce': oauth2.generate_nonce(),
                'oauth_timestamp': oauth2.generate_timestamp(),
                'oauth_token': self.token,
                'oauth_consumer_key': self.consumer_key
            }
        )
        oauth_token = oauth2.Token(self.token, self.token_secret)
        oauth_request.sign_request(oauth2.SignatureMethod_HMAC_SHA1(), consumer,
                                   oauth_token)
        signed_url = oauth_request.to_url()

        return signed_url


class YelpApiError(Exception):
    """
    Error to be thrown by the API
    """

    def __init__(self, msg):
        self.msg = msg

    def __str__(self):
        return repr(self.msg)
