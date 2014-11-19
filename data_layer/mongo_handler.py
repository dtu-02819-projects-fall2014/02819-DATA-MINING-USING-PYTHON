# -*- coding: utf-8 -*-

import pymongo

class YelpMongoHandler():


    def __init__(self, collection, port=27017, host='localhost'):
        
        client = pymongo.MongoClient(host,port)
        self.db=client.yelp_db

        self.collection = self.get_collection(collection)


    def get_collection(self,collection):

        if type(collection) != str :
            raise Error('collection argument has to be a string')    

        if collection == 'users_info':
            return self.db.users_info

        elif collection == 'places':
            return self.db.places

        elif collection == 'users_id':
            return self.db.users_id

        elif collection == 'frontend_users':
            return self.db.frontend_users
        
        else:
            raise Error('Collection %s not exist' %(collection))    


        
    def get_documents( self, query={}, one=False ):
        if one:
            return self.collection.find_one(query)
        else:
            return [ doc for doc in self.collection.find(query) ]



    def add_document( self, doc, update=False ):

        if '_id' not in doc.keys():
            raise Error('document must have an id in form of "_id" ')    

        _return = {'_id':doc['_id'], 'updated':False, 'inserted':False}
            
        if self.collection.find_one({'_id':doc['_id']}) != None:
            
            if update:
                self.collection.update({ '_id':doc['_id'] }, { "$set" : doc } )
                _return['updated'] = True
                
        else:
            self.collection.insert(doc)
            _return['inserted'] = True

        return _return
