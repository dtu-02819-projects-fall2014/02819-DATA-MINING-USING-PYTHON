from flask import Flask, jsonify
import json
import yelp_json
# from user_scraper import get_user
from flask import render_template, url_for, request
from random import shuffle
import helper_functions

app = Flask(__name__, static_url_path = '/static')



@app.route('/')
def home():
    return render_template('index.html')



@app.route('/ratings/',methods = ['POST', 'GET'])
@app.route('/ratings/<count>',methods = ['POST', 'GET'])
def by_ratings(count=5):

    places = None
    suggestions = None
    log = None

    if request.method == 'GET':
        places = helper_functions.get_places()
        shuffle(places)
        places=places[:min(int(count),20)]

    if request.method == 'POST':
        #values of form [ ( place_id, rating ), ... ]
        values = request.form.items()


        log=helper_functions.add_ratings_to_db(values)
        
        #only return the user for the moment
        suggestions =  helper_functions.get_suggestions_ratings(log['_id'])
            
    return render_template('ratings.html', places=places, suggestions = suggestions, log=log)


@app.route('/user/',methods = ['POST', 'GET'])
def by_user_name():
    name = None
    error = None
    suggestions = None

    if request.method == 'POST':
        name = str(request.form['name'])
        suggestions = helper_functions.get_suggestions_username(name)
        if not suggestions:
            error = "No user with name %s in database"%(name)

    return render_template('user.html', name=name, suggestions = suggestions, error = error)





if __name__ == '__main__':

    app.run(debug=True)
    
