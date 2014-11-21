# -*- coding: utf-8 -*-

"""

"""
import json
import urllib
import urllib2
import oauth2


class YelpApiDataExtractor:
    """

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
