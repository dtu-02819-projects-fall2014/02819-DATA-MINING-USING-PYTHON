# -*- coding: utf-8 -*-


"""
Usage:
     reduce_db.py 
     reduce_db.py <min_mentionned>
      
"""


import mongo_handler
from docopt import docopt
from pymongo.errors import ConnectionFailure

def reduce_places(min_mentionned=2):
    


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

if __name__ == '__main__':

    try:
        args = docopt(__doc__, version='reduce_db 1.0')
         
        if args['<min_mentionned>'] is not None:
          print reduce_places(min_mentionned=int(args['<min_mentionned>']))
        else:
          print reduce_places()

    except ConnectionFailure as e1:
        print '{} check MongoDB connection'.format(e1)
   
