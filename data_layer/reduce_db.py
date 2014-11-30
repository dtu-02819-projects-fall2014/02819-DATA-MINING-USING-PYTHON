# -*- coding: utf-8 -*-


"""
Usage:
     reduce_db.py 
     reduce_db.py <min_mentionned>
      
"""


import mongo_handler
from docopt import docopt
from pymongo.errors import ConnectionFailure

def _reduce_places(min_mentionned=2):
    
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
        if places[_id] < min_mentionned:
            if handler.remove('places', {'_id': _id }, multiple=False)['n'] > 0:
                number_of_deleted +=1

    return number_of_deleted

def _reduce_reviews(collection = 'users_info'):
    if collection is not 'users_info' and not 'frontend_users':
        raise Exception('collection argument has to be users_info or frontend_users')

    handler = mongo_handler.YelpMongoHandler()
    reviews_deleted = 0
    users_deleted = 0
    for u in handler.get_documents(collection):
        reviews = []
        for r in u['reviews']:
            _id = r['_id']
            if  handler.get_documents('places', query={'_id':_id}, one=True):
                reviews.append(r)
            else:
                reviews_deleted +=1

        if len(reviews) == 0:
            handler.remove(collection, {'_id':u['_id']}, multiple=False)
            users_deleted +=1
        else:
            u['reviews'] = reviews
            handler.add_document(u, collection, update=True)

    return {'reviews_deleted': reviews_deleted, 'users_deleted': users_deleted}  

if __name__ == '__main__':

    try:
        args = docopt(__doc__, version='reduce_db 1.0')
         
        s = 'number of deleted places'
        if args['<min_mentionned>'] is not None:
          print s, _reduce_places(min_mentionned=int(args['<min_mentionned>']))
        else:
          print s, _reduce_places()
          
        s2 = 'infos in collection'
        print s2, 'users_info:', _reduce_reviews()
        print s2, 'frontend_users:', _reduce_reviews(collection='frontend_users')

    except ConnectionFailure as e1:
        print '{} check MongoDB connection'.format(e1)
   
