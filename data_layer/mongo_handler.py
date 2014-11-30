# -*- coding: utf-8 -*-

import pymongo


class YelpMongoHandler():

    def __init__(self, port=27017, host='localhost'):
        client = pymongo.MongoClient(host, port)
        self.db = client.yelp_db

    def get_collection(self, collection):

        if type(collection) is not str:
            raise Exception('collection argument has to be a string')

        if collection == 'users_info':
            return self.db.users_info

        elif collection == 'places':
            return self.db.places


        elif collection == 'frontend_users':
            return self.db.frontend_users
        else:
            raise Exception('Collection %s not exist' % (collection))

    def get_documents(self, collection, query={}, one=False):
        if one:
            return self.get_collection(collection).find_one(query)
        else:
            return [doc for doc in self.get_collection(collection).find(query)]

    def add_document(self, doc, collection, update=False):

        if '_id' not in doc.keys():
            raise Exception('document must have an id in form of "_id" ')

        m_collection = self.get_collection(collection)
        _id = doc['_id']
        return_value = {'_id': _id, 'updated': False, 'inserted': False}
        if m_collection.find_one(
                {'_id': _id}) is not None:

            if update:
                m_collection.update(
                    {'_id': _id}, {"$set": doc})
                return_value['updated'] = True
        else:
            m_collection.insert(doc)
            return_value['inserted'] = True

        return return_value

    def drop_collection(self, collection):
        """
        Drops the collections in the db

        Args:
            collection (str): The collection to drop
        """
        return self.get_collection(collection).drop()
        

    def remove(self, collection, query, multiple=True):
        
        return self.get_collection(collection).remove(query, multi=multiple)
        
    
