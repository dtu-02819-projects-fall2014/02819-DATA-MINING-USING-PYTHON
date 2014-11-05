# -*- coding: utf-8 -*-

from restaurant_scraper import scrap_users
from user_scraper import get_user
import yelp_json
from pymongo import MongoClient

CONSUMER_KEY = 'Fo0uLsgv__5F6ZK9e-zokQ'
CONSUMER_SECRET = 'wNPVw-bakq4mz6_Nv3EcfkvXku0'
TOKEN = 'j4JkPkbIQ51MKn_Ie1jDO6uvC3TWavsX'
TOKEN_SECRET = 'czOE7mgVVsRUl9bzuGe4Bn_xXlk'

client=MongoClient('localhost',27017)
db=client.yelp_db
users_id=db.users_id


def search_r_urls(place_type,location, count):
    extractor = yelp_json.YelpApiDataExtractor(CONSUMER_KEY,CONSUMER_SECRET,TOKEN,TOKEN_SECRET)
    json = extractor.query_api(place_type, location, count)
    urls=[ r['url'] for r in json ]
    return urls



def get_users_id(place_type='restaurant',location='copenhagen', count=10):
    urls=search_r_urls(place_type,location,count)
    
    #inserted in db inside the scrap_users func should we populate the db here instead?
    users_id=[ scrap_users(url).keys() for url in urls ]
    
    
    return users_id

def get_users_info(number=None):
    users_info=[]
    ##for testing
    if number:
        count=0
        for u in users_id.find():
            if count is number:
                return users_info
            count+=1
            print 'getting user informations from',u.get('name')
            users_info.append(get_user(u.get('_id')))
    ##

        
    for u in users_id.find():
        print 'getting user informations from',u.get('name')
        #inserted in db inside the get_user func should we populate the db here instead?
        users_info.append(get_user(u.get('_id')))
        
    
    

    return users_info

