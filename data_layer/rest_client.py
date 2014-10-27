from flask import Flask, jsonify
import pymongo
from pymongo import MongoClient
import json
import yelp_json
from user_scraper import get_user

client=MongoClient('localhost',27017)
db=client.flask_db
search=db.search

app = Flask(__name__)



CONSUMER_KEY = 'Fo0uLsgv__5F6ZK9e-zokQ'
CONSUMER_SECRET = 'wNPVw-bakq4mz6_Nv3EcfkvXku0'
TOKEN = 'j4JkPkbIQ51MKn_Ie1jDO6uvC3TWavsX'
TOKEN_SECRET = 'czOE7mgVVsRUl9bzuGe4Bn_xXlk'


@app.route('/')
def hello_world():
    return 'Hi'

    

@app.route('/search:<place_type>-<location>-<count>')
def search(place_type='dinner',location='New York', count=10):
    extractor = yelp_json.YelpApiDataExtractor(CONSUMER_KEY,CONSUMER_SECRET,TOKEN,TOKEN_SECRET)
    json = extractor.query_api(place_type, location, count)
    return jsonify({'json':json})

@app.route('/search')
def s():
    return search()

@app.route('/search_urls:<place_type>-<location>-<count>')
def search_urls(place_type='dinner',location='New York', count=10):
    extractor = yelp_json.YelpApiDataExtractor(CONSUMER_KEY,CONSUMER_SECRET,TOKEN,TOKEN_SECRET)
    json = extractor.query_api(place_type, location, count)
    urls = [elem['url'] for elem in json]
    return jsonify({'urls':urls})

@app.route('/search_urls')
def s_urls():
    return search_urls()

@app.route('/user:<id>')
def user(id):
    user_data = get_user(id)
    return jsonify({'user':user_data})


if __name__ == '__main__':
    app.run(debug=True)
