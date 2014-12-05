# -*- coding: utf-8 -*-


"""
Usage:
    reduce_db.py
    reduce_db.py <min_mentionned>

"""

"""
This script reduces the number of places in the data base and in the reviews.
It is necessary that every restaurant is mentionned by more than one user
in order for the suggestions algorithm to work.

"""

import mongo_handler
from docopt import docopt
from pymongo.errors import ConnectionFailure


def _reduce_places(min_mentionned=5):
    """
    The function deletes every place from the data base that is
    mentionned by less than 'min_mentionned' users.

    Kwargs:
        min_mentionned (int): Specify the minimal amount of users that
        mention a place in their reviews.

    Return:
        The number of deleted places from the data base
    """

    handler = mongo_handler.YelpMongoHandler()

    places = {}
    for u in handler.get_documents('users_info'):
        for r in u['reviews']:
            _id = r['_id']
            if _id in places.keys():
                places[_id] += 1
            else:
                places[_id] = 1

    number_of_deleted = 0
    for _id in places.keys():
        if places[_id] <= min_mentionned:
            # The 'n' field specifies the number of deleted places
            if handler.remove('places', {'_id': _id}, multiple=False)['n'] == 1:
                number_of_deleted += 1

    return number_of_deleted


def _reduce_reviews(collection='users_info'):
    """
    The function deletes every review that mention the deleted places.
    It deletes a user if it has no reviews anymore.

    Kwargs:
        collection (str): Specify the collection of users to use. Can be
        'users_info' or 'frontend_users'. Initial is 'users_info'.

    Return:
        A dictionary with two fields:  {'reviews_deleted': (int),
        'users_deleted': (int)}.

    Raise:
        An Exception if the collection parameter is not 'users_info' or
        'frontend_users'
    """

    if collection is not 'users_info' and not 'frontend_users':
        raise Exception('collection argument has to be users_info or'
                        'frontend_users')

    handler = mongo_handler.YelpMongoHandler()

    reviews_deleted = 0
    users_deleted = 0
    for u in handler.get_documents(collection):
        reviews = []
        for r in u['reviews']:
            _id = r['_id']
            if handler.get_documents('places', query={'_id': _id}, one=True):
                reviews.append(r)
            else:
                reviews_deleted += 1

        # if zero reviews left for the user, then it has to be deleted
        if len(reviews) == 0:
            handler.remove(collection, {'_id': u['_id']}, multiple=False)
            users_deleted += 1
        # else we update the user with his reduced list of reviews
        else:
            u['reviews'] = reviews
            handler.add_document(u, collection, update=True)

    return {'reviews_deleted': reviews_deleted, 'users_deleted': users_deleted}


if __name__ == '__main__':

    try:
        args = docopt(__doc__, version='reduce_db 1.0')

        s = 'number of deleted places'
        if args['<min_mentionned>'] is not None:
            print s, _reduce_places(min_mentionned=int(
                args['<min_mentionned>']))
        else:
            print s, _reduce_places()

        s2 = 'infos in collection'
        print s2, 'users_info:', _reduce_reviews()
        print s2, 'frontend_users:', _reduce_reviews(
            collection='frontend_users')

    except ConnectionFailure as e1:
        print '{} check MongoDB connection'.format(e1)
