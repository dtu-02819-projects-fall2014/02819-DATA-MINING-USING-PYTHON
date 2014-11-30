from flask import Flask, jsonify
import json
import yelp_json
# from user_scraper import get_user
from flask import render_template, url_for, request
import helper_functions

app = Flask(__name__, static_url_path = '/static')



@app.route('/')
def home():
    db_infos = { 'number_of_places': len(helper_functions.get_number_of_places()), 'number_of_users': helper_functions.get_number_of_users() }
    return render_template('index.html', db_infos = db_infos)



@app.route('/ratings/',methods = ['POST', 'GET'])
@app.route('/ratings/<count>',methods = ['POST', 'GET'])
def by_ratings(count=5):

    places = None
    suggestions = None
    log = None
    error = None

    if request.method == 'GET':
        places = helper_functions.get_some_places(count)

    if request.method == 'POST':
        #values of form [ ( place_id, rating ), ... ]
        values = request.form.items()

        #return value of the mongo_handler add_document function
        log = helper_functions.add_ratings_to_db(values)
        
        try :
            suggestions =  helper_functions.get_suggestions_ratings(log['_id']) [:count]
        except Exception as e:
            error = str(e)

    return render_template('ratings.html', places=places,
                           suggestions=suggestions, log=log, error=error, count=count)


@app.route('/user/',methods = ['POST', 'GET'])
@app.route('/user/<count>',methods = ['POST', 'GET'])
def by_user_name( count = 5):
    name = None
    error = None
    suggestions = None
    users = None
 
    if request.method == 'GET':
        users = helper_functions.get_some_user_names()

    if request.method == 'POST':
        name = str(request.form['name'])
        try :
            suggestions = helper_functions.get_suggestions_username(name) [:count]
        except Exception as e:
            error = str(e)
            
    return render_template('user.html', name=name, suggestions = suggestions, error = error, users=users, count=count)





if __name__ == '__main__':

    app.run(debug=True)
    
