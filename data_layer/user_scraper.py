# -*- coding: utf-8 -*-
import urllib2
from bs4 import BeautifulSoup


class UserScraper:

    def __init__(self):
        self.places = []
        self.users = []
        self.soups = {}
        self.soups_city = {}

    def soup_reviews(self, user_id, page_start):
        url = 'http://www.yelp.com/user_details_reviews_self?userid=%s'\
            '&rec_pagestart=%d' % (user_id, page_start)
        content = urllib2.urlopen(url).read()
        return BeautifulSoup(content)

    def soup_friends(self, user_id):
        friends_url = 'http://www.yelp.com/user_details_friends?userid=%s'\
            % (user_id)
        content = urllib2.urlopen(friends_url).read()
        return BeautifulSoup(content)

    def put_it(self, user_id, city):
        """

        """
        include_last_page = 1
        soup = self.soup_reviews(user_id, 0)
        pages = [soup]

        # partition page_interval in tens
        page_interval = self.get_number_of_pages(soup)/10

        for page in xrange(page_interval+include_last_page):
            if page is not 0:
                soup = self.soup_reviews(user_id, page*10)
                pages.append(soup)

        self.soups[user_id] = pages
        self.soups_city[user_id] = []

    def scrap_users_places(self, city):
        """

        """
        for user, soups in self.soups.items():
            for soup in soups:
                for review in soup.find_all('div', class_='review'):
                    address = self.extract_address(review)
                    if city in address['address']:
                        self.soups_city[user].append(review)
                        id_name = self.extract_id_and_name(review)
                        price_category = self.extract_price_and_category(review)

                        merge_dicts = reduce(lambda d1, d2: dict(d1, **d2),
                                             (id_name, address, price_category))

                        self.places.append(merge_dicts)

    def scrap_users_reviews(self):
        """

        """
        for user, reviews in self.soups_city.items():
            user_reviews = []
            user_info = self.extract_user_information(user)

            for review in reviews:
                id_name = self.extract_id_and_name(review)
                rating_review = self.extract_rating(review)
                merge_dicts = dict(id_name.items() + rating_review.items())
                user_reviews.append(merge_dicts)

            self.users.append({'_id': user,
                               'location': user_info['location'],
                               'created_at': user_info['created_at'],
                               'reviews': user_reviews})

    def extract_user_information(self, user_id):
        location = self.soups[user_id][0].find(
            'div', id='profile_questions').find_all('p')[0].get_text(
            ).replace('\n', '').strip()

        creates_at = self.soups[user_id][0].find(
            'div', id='profile_questions').find_all(
                'p')[1].get_text().replace('\n', '').strip()

        return {'location': location, 'created_at': creates_at}

    def get_number_of_pages(self, soup_snippet):
        """

        """
        return int(soup_snippet.find(
            'td', class_='range-of-total').get_text().strip().split(' ')[-1])

    def replace_all(self, text, dic):
        for i, j in dic.iteritems():
            text = text.replace(i, j)
        return text

    def extract_address(self, soup_snippet):
        """
        bs4.element.Tag
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

    def extract_id_and_name(self, soup_snippet):
        """

        """
        hash_value = soup_snippet.find(
            'a', class_="biz-name").get('data-hovercard-id')

        name = soup_snippet.find('a', class_='biz-name').get_text()

        return {'_id': hash_value, 'name': name}

    def extract_price_and_category(self, soup_snippet):
        """

        """
        price_category_list = soup_snippet.find(
            'div', class_='price-category').get_text().split('\n')

        # clean up the list
        price_category_list = [i for i in price_category_list if i is not u'']
        category_index = 0 if len(price_category_list) is 1 else 1
        price_category_list[category_index] = [
            i.strip() for i in price_category_list[category_index].split(',')]

        # translate the yelp price symbol into a integer, if price exists
        if category_index > 0:
            price_category_list[0] = len(price_category_list[0])

            return {'price': price_category_list[0],
                    'categories': price_category_list[category_index]}

        return {'categories': price_category_list[category_index]}

    def extract_rating(self, soup_snippet, review_length=100):
        """

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
