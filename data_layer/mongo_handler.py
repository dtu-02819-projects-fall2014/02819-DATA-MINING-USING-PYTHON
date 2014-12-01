# -*- coding: utf-8 -*-

import pymongo


class YelpMongoHandler():
    """
    The YelpMongoHandler class is a small Mongo handler for our project.
    It allows to access and modify the database more easily. It support the
    collections that we use, i.e. 'users_info', 'places' and 'frontend_users'.
    The 'users_info' collection describes all the scrapped users.
    The 'places' collection describes the scrapped places.
    The 'frontend_collection' represent all the users created automatically
    from the web page.

    Fields:
         db: the 'yelp_db' that contains the three above mentionned collections
    """

    def __init__(self, port=27017, host='localhost'):
        client = pymongo.MongoClient(host, port)
        self.db = client.yelp_db

    def get_collection(self, collection):
        """
         Returns a collection according to the string passed in parameter

         Args:
             collection (str): The name of the desired collection

         Return:
             One of the three collections according to the parameter

         Raise:
             An exception if the collection parameter is not a string and not
             one of these values:
             ['users_info', 'places', 'frontend_users']
         """

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
        """
        The functions retrieves one or more documents of a collection

        Args:
            collection (str): The name of the collection to get documents

        Kwargs:
            query (dict): The query for the desired document.
            Is initial empty dict.
            one (bool): If True returns only one document. Is initial False.

        Return:
             A dict or a list of dicts according to the query and the
             given collection
         """

        if one:
            return self.get_collection(collection).find_one(query)
        else:
            return [doc for doc in self.get_collection(collection).find(query)]

    def add_document(self, doc, collection, update=False):
        """
        The function add or update a document in agiven collection

        Args:
            collection (str): The name of the collection where to add a document
            doc (dict): The document to add

        Kwargs:
            update (bool): if True will update an existing document.
            Is initial False.
        Return:
             A dictionary with three fields: {'_id': (str), 'updated': (bool),
             'inserted': (bool)}

        Raise:
             An exception if the document has no '_id' field
        """

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
        """
        The function removes documents from a collection

        Args:
            collection (str): The name of the desired collection
            query (dict): The query of the documents to remove

        Kwargs:
            multiple (bool): if False will remove only one document that matches
            the query. Is initial True.

        Return:
             A dictionary with two fields: {'n': (int), 'ok': (int)}
        """

        return self.get_collection(collection).remove(query, multi=multiple)
