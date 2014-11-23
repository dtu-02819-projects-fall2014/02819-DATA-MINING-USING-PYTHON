# -*- coding: utf-8 -*-
import urllib2
from bs4 import BeautifulSoup
import re
import time
import random


class UserScraper:
    """
    The UserScraper class includes tools for scraping the Yelp users places and
    the review of those. After class instantiation, run the srap_users method
    import populate_db
    with a list of user ids. Afterwords you will be able to get a list
    containing dictionaries of places the users have visited and a list
    containing dictionaries with the users and the reviews.

    Fields:
        places: List containing dictionaries of places the users have visited
        users: List containing dictionaries with the users and the reviews.
    """

    def __init__(self):
        self.places = []
        self.users = []
        self.__soups = {}
        self.__soups_city = {}
        self.__place_record = set()

    def scrap_users(self, city, filter_state, users_ids):
        """
        The method has to be invoked to start the scraping of the places and
        the review of the Yelp users

        Args:
            city (str): Specify which city the place and reviews has to come
            from to be scrapped
            user_ids (str list): A list containing all the users hashcode,
            which the scraper should extract places and reviews from.
            filter_state (str): The Yelp fiter state, f.eks. Copenhagen is
            '84', paris is '75', New York is 'NY'
        """
        include_last_page = 1

        for user_id in users_ids:
            print('Start downlaoding user {0}'.format(user_id))

            soup = self.soup_reviews_by_filter(user_id, 0, city, filter_state)

            page_interval = self.get_number_of_pages(soup)

            if page_interval is None:
                continue

            # partition page_interval in tens
            page_interval /= 10

            pages = [soup]

            for page in xrange(page_interval+include_last_page):
                # sleep the thread a few seconds inorder not to spam yelp
                self.__sleep_rand()
                
                print('Start downloading page {0} of {1}'.format(
                    page+1, page_interval+1))

                if page is not 0:
                    soup = self.soup_reviews_by_filter(
                        user_id, page*10, city, filter_state)
                    pages.append(soup)

            self.__soups[user_id] = pages

            # loads the users in, to prepare for soups for the specific city
            self.__soups_city[user_id] = []

            print('User {0} pages are downloadet'.format(user_id))

        print('Download done - Start processing data...')

        self.__scrap_users_places()
        self.__scrap_users_reviews()

    def __sleep_rand(self):
        """
        Makes the thread sleep a few seconds
        """
        a = random.uniform(0.5, 1)
        time.sleep(a)

    def __scrap_users_places(self):
        """
        Scrap a users places of a specific city. Every time the method scrap a
        place, it save the soup of places review in an internal dictionary
        with the user_id as the key.

        """
        for user, soups in self.__soups.items():
            for soup in soups:
                for review in soup.find_all('div', class_='review'):
                    address = self.extract_address(review)
                    self.__soups_city[user].append(review)
                    id_name = self.extract_information(review)

                    if id_name['_id'] in self.__place_record:
                            continue

                    self.__place_record.add(id_name['_id'])

                    price_category = self.extract_price_and_category(review)

                    merge_dicts = reduce(lambda d1, d2: dict(d1, **d2),
                                         (id_name, address, price_category))

                    self.places.append(merge_dicts)

    def __scrap_users_reviews(self):
        """
        Scrapping all the soups that is in the internal soups_city
        dictionnaire, and generating a list of dictionnaire containing
        reviews and user information.
        """
        for user, reviews in self.__soups_city.items():
            user_reviews = []
            user_info = self.__extract_user_information(user)
            user_votes = self.__extract_votes(user)

            for review in reviews:
                id_name = self.extract_information(review)
                rating_review = self.extract_rating(review)
                merge_dicts = dict(id_name.items() + rating_review.items())
                user_reviews.append(merge_dicts)

            review_count = len(user_reviews)

            self.users.append({'_id': user,
                               'location': user_info['location'],
                               'created_at': user_info['created_at'],
                               'reviews': user_reviews,
                               'total_review_count': review_count,
                               'review_votes': user_votes})

    def soup_reviews_by_filter(self, user_id, page_start, city, filter_state):
        """
        Generate a url to the specific user review page, from a specified city

        Args:
            user_id (str): The hashcode of the user
            page_start: Which user review site to start at, shold
            be divisible with ten, to avoid missing som reviews.
            filter_state (str): The Yelp fiter state, f.eks. Copenhagen is
            '84', paris is '75', New York is 'NY'

        Return:
            str -- The url to the user review page
        """
        url = 'http://www.yelp.com/user_details_reviews_self?userid=%s'\
            '&review_filter=location&location_filter_city=%s'\
            '&location_filter_state=%s&rec_pagestart=%d'\
            % (user_id, city, filter_state, page_start)
        openUrl = urllib2.urlopen(url.encode('utf-8'))
        content = openUrl.read()
        return BeautifulSoup(content)

    def soup_friends(self, user_id):
        """
        Generate a url to the users friends

        Args:
            user_id (str): The hashcode of the user

        Return:
            str -- The url to the users friends
        """
        friends_url = 'http://www.yelp.com/user_details_friends?userid=%s'\
            % (user_id)
        content = urllib2.urlopen(friends_url).read()
        return BeautifulSoup(content)

    def get_number_of_pages(self, soup_snippet):
        """
        Returns the number of pages on the users review page

        Args:
            soup_snippet (bs4.element.Tag): bs4 tag containing
            the review page

        Return:
            int -- The number of pages
        """
        range_of_total = soup_snippet.find('td', class_='range-of-total')

        # the user might not have any reviews
        if range_of_total is None:
            return None

        return int(range_of_total.get_text().strip().split(' ')[-1])

    def replace_all(self, text, dic):
        """
        Replaces all elements in a string

        Args:
            text (str): The text which the replacement should be invoked at
            dic (dict): A dictionary where the key specify what should be
            replaced and the element that specify what should be put in
            instead.

        Return:
            str -- The replaces text string
        """
        for i, j in dic.iteritems():
            text = text.replace(i, j)
        return text

    def __extract_user_information(self, user_id):
        """
        Utillize the internal soups dict with the users pages to find
        the information of the user.

        Args:
            user_id (str): The users hash is used af key in the dict
            to find the correct page list.

        Return:
            dict -- Dict object with the key 'location' and 'created_at'
        """
        location = self.__soups[user_id][0].find(
            'div', id='profile_questions').find_all('p')[0].get_text(
            ).replace('\n', '').strip()

        creates_at = self.__soups[user_id][0].find(
            'div', id='profile_questions').find_all(
                'p')[1].get_text().replace('\n', '').strip()

        return {'location': location, 'created_at': creates_at}

    def extract_address(self, soup_snippet):
        """
        Given a soup snippet, the method finds the address of the
        place in the snippet, and wraps it in a dict.

        Args:
            soup_snippet (bs4.element.Tag): The soup snippet that should
            be search through.

        Return:
            A dict object with 'address' as key
        """
        soup_snippet_string = str(soup_snippet.find('address'))

        # Deals with all the first addr lines in address string,
        # last address line is a special case
        cleaned_addr_list = self.replace_all(
            soup_snippet_string, {'\n': '',
                                  '<br>': ',',
                                  '<address>': ''}).strip().split(',')[:-1]

        return {'address': ' '.join(
            item.decode('utf-8') for item in cleaned_addr_list)}

    def extract_information(self, soup_snippet):
        """
        Given a soup snippet, the method finds the place information of the
        place in the snippet, and wraps it in a dict.

        Args:
            soup_snippet (bs4.element.Tag): The soup snippet that should
            be search through.

        Return:
            A dict object with '_id' as key, corresponds to the hash code of
            place and 'name' as key

        """
        hash_value = soup_snippet.find(
            'a', class_="biz-name").get('data-hovercard-id')

        name = soup_snippet.find('a', class_='biz-name').get_text()

        url = u'http://www.yelp.dk{0}'.format(soup_snippet.find(
            'a', class_='biz-name').get('href'))

        return {'_id': hash_value, 'name': name, 'url': url}

    def extract_price_and_category(self, soup_snippet):
        """
        Given a soup snippet, the method finds the price and category of the
        place in the snippet, and wraps it in a dict.

        Args:
            soup_snippet (bs4.element.Tag): The soup snippet that should
            be search through.

        Return:
            A dict object with 'price', and 'categories' as keys
        """
        price_category_list = soup_snippet.find(
            'div', class_='price-category').get_text().split('\n')

        # clean up the list
        price_category_list = [i for i in price_category_list if i is not u'']

        try:
            category_index = 0 if len(price_category_list) is 1 else 1

            price_category_list[category_index] = [
                i.strip() for i in price_category_list[
                    category_index].split(',')]

            # translate the yelp price symbol into a integer, if price exists
            if category_index > 0:
                price_category_list[0] = len(price_category_list[0])

                return {'price': price_category_list[0],
                        'categories': price_category_list[category_index]}

        except IndexError:
            return {'price': None,
                    'categories': None}

        return {'price': None,
                'categories': price_category_list[category_index]}

    def extract_rating(self, soup_snippet, review_length=100):
        """
        Given a soup snippet, the method finds the users rating of his/hers
        places, and also extract the first n characters of the the review text.
        Furthermore it also extract the date the review was written.

        Args:
            soup_snippet (bs4.element.Tag): The soup snippet that should
            be search through.

        Kwargs:
            review_length (int): Defines the number of charactors the method
            should grab from the review. Is initial 100.

        Return:
            A dict object with 'rating', 'created_at' and 'text' as keys

        """
        rating = float(soup_snippet.find(
            'div', class_='rating-very-large').find(
            'i').get('title').split(' ')[0])

        rating_date = soup_snippet.find(
            'span', class_='rating-qualifier').get_text().strip()

        rating_text = soup_snippet.find(
            'div', class_='review-content').find('p').get_text()[:review_length]

        return {'rating': rating,
                'created_at': rating_date,
                'text': rating_text}

    def __extract_votes(self, user_id):
        """
        Utillize the internal soups dict with the users pages to find
        the votes by the  user.

        Args:
            user_id (str): The users hash is used af key in the dict
            to find the correct page list.

        Return:
            dict -- Dict object with the key 'usefull', 'funny' and
            'cool'

        """
        search_str = 'i-wrap ig-wrap-user_social '\
            'i-review-votes-user_social-wrap smaller'

        first_user_page = self.__soups[user_id][0]

        vote = first_user_page.find('p', class_=search_str)

        # The user might not have given any votes
        if vote is None:
            return {'usefull': None, 'funny': None, 'cool': None}

        vote_str = vote.get_text()
        votes = map(int, re.findall('\d+', vote_str))

        rev_votes = {}
        rev_votes['usefull'], rev_votes['funny'], rev_votes['cool'] = votes

        return rev_votes
