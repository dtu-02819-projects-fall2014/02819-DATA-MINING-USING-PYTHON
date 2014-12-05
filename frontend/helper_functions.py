
"""
Helper functions for the web client.
Links the database, the web client and the recommendations algorithm
"""

from os import (path, sys)
parentdir = path.dirname(path.dirname(path.abspath(__file__)))
sys.path.insert(0, parentdir)
from data_layer import mongo_handler
from pymongo.errors import ConnectionFailure
import recommendations
import datetime
from random import shuffle

try:
    handler = mongo_handler.YelpMongoHandler()
except ConnectionFailure as e:
    print('Cannot connect to mongodb %s' % e)
    sys.exit


def add_ratings_to_db(values):

    """
    Create and adds an anonym user to the frontend_users collection,
    according to the ratings form.

    Args:
        values (tuple): ((str) _id, (str) rating)

    Return:
        A three field dictionary: {'_id': (str),
        'updated': (bool), 'inserted': (bool)}

    """
    user = {}
    reviews = []

    for v in values:
        place = handler.get_documents(
            'places', one=True, query={'_id': v[0]})
        review = {}
        review['_id'] = place['_id']
        review['name'] = place['name']
        review['rating'] = float(v[1])
        reviews.append(review)

    user['reviews'] = reviews
    user['name'] = "anonym"
    # ID generated with the current date
    user['_id'] = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S.%f")[:-3]

    return_value = handler.add_document(user, 'frontend_users')

    return return_value


def get_some_places(count):
    """
    The function gives randomly a given number of places

    Args:
        count (int): The number of wanted places

    Return:
        A list of places

    """

    places = handler.get_documents('places')
    shuffle(places)
    places = places[:min(int(count), 20)]
    return places


def get_some_user_names(count=5):
    """
    The function gives randomly a given number of real users

    Args:
        count (int): The number of wanted real users

    Return:
        A list of real users

    """

    users = handler.get_documents('users_info')
    shuffle(users)
    users = users[:min(int(count), 20)]
    return [u['name'] for u in users]


def get_number_of_users():
    """
    The function gives the total number of users: anonym and real users

    Return:
        The total number of users stored in the data base

    """

    return len(handler.get_documents('users_info')) + len(
        handler.get_documents('frontend_users'))


def get_number_of_places():
    """
    The function gives the number of places

    Return:
        The number places stored in the data base

    """

    return len(handler.get_documents('places'))


def get_user_reviews(name):
    """
    The function gives the reviews from a user name.

    Args:
        name (dict): a yelp user in the database

    Return:
        A dictionary discribing the reviews for a yelp user if it exist in the
        db

    """

    user = _get_user_by_name(name)

    ratings = {}
    for r in user['reviews']:
        ratings[r['name']] = float(r['rating'])

    return {user['name']: ratings}


def _get_user_by_name(name):
    """
    The function gives the user from a user name.

    Args:
        name (str): The name of a yelp user in the database

    Return:
        The suggestions for a yelp user

    Raise:
        An Exception if the user is not in the db
    """

    user = handler.get_documents('users_info', one=True, query={'name': name})

    if not user:
        raise Exception("No user found with the name %s" % (name))

    return user


def get_suggestions_ratings(_id):
    """
    The function gives the suggestions from the ratings.

    Args:
        _id (str): The id of an anonym user

    Return:
        The suggestions for an anonym user

    """

    user = handler.get_documents('frontend_users', one=True, query={'_id': _id})

    return _suggestions(user)


def get_suggestions_username(name):
    """
    The function gives the suggestions from a user name.

    Args:
        name (str): The name of a yelp user in the database

    Return:
        The suggestions for a yelp user
    """

    return _suggestions(_get_user_by_name(name))


def _suggestions(user):
    """
    The function gives the suggestions for a given user, by calling the
    recommendation algorithm.

    Args:
        user (dict): An anonym or real user existing in the data base.

    Return:
        The suggestions for the user.

    Raise:
        An Excpetion if no suggestions are available.
    """

    users = handler.get_documents('users_info') + handler.get_documents(
        'frontend_users')

    prefs = {}
    for u in users:
        prefs.update(_transform_for_suggestions(u))

    reco_ids = recommendations.getRecommendations(prefs, user['_id'])
    method = "pearson"
    # if no recommendation found with pearson sim
    # distance we use the euclidean instead
    if not reco_ids:
        method = "euclidean"
        reco_ids = recommendations.getRecommendations(
            prefs, user['_id'], recommendations.sim_distance)

    suggestions = []
    for score, place_id in reco_ids:
        place = handler.get_documents('places', one=True,
                                      query={'_id': place_id})
        place['score'] = score
        suggestions.append(place)

    if not suggestions:
        raise Exception("No suggestions available")

    return (suggestions, method)


def _transform_for_suggestions(user):
    """
    The function transform an user dictionary in a dictionary that fits for
    the recommendations algorithm

    Args:
        user (dict): An anonym or real user existing in the data base.

    Return:
        A dictionary with one key:
            { <user_id (str)> : <ratings (list of dict)> }.
        'ratings' is a list of dictionaries with one key:
            { <the_id_of_the_place (str)> : <rating (int)> }
    """

    ratings = {}
    for r in user['reviews']:
        ratings[r['_id']] = float(r['rating'])
    return {user['_id']: ratings}
