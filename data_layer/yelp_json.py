# -*- coding: utf-8 -*-

"""

"""
import json
import urllib
import urllib2
import oauth2

API_HOST = 'api.yelp.com'
SEARCH_PATH = '/v2/search/'


class YelpApiDataExtractor:
    """

    """

    def __init__(self, consumer_key, consumer_secret, token, token_secret):
        self.consumer_key = consumer_key
        self.consumer_secret = consumer_secret
        self.token = token
        self.token_secret = token_secret

    def query_api(self, term, location, search_limit):
        """

        """
        response = self.__search(term, location, search_limit)

        businesses = response.get('businesses')

        if not businesses:
            print('No businesses for {0} in {1} found.'.format(term, location))
            return

        return businesses

    def __search(self, term, location, search_limit):
        """

        """

        url_params = {
            'term': term,
            'location': location,
            'limit': search_limit
        }

        return self.__request(API_HOST, SEARCH_PATH, url_params=url_params)

    def __request(self, host, path, url_params=None):
        """

        """
        url_params = url_params or {}
        encoded_params = urllib.urlencode(url_params)

        url = 'http://{0}{1}?{2}'.format(host, path, encoded_params)

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

        connection = urllib2.urlopen(signed_url, None)
        try:
            response = json.loads(connection.read())
        finally:
            connection.close()

        return response
