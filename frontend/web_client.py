# -*- coding: utf-8 -*-

"""
Flask web client, shows informations and suggestions in the web browser
use helper_functions.py
css framework: skeleton - http://getskeleton.com/

"""
from flask import (Flask, render_template, request)
import helper_functions

app = Flask(__name__, static_url_path='/static')


@app.route('/')
def home():
    """
    Shows Home page with some informations about the database, i.e. number of
    users and places

    Request Methods:
        'GET'

    Urls:
        '/'

    Return:
        render template 'index.html'

    """
    db_infos = {'number_of_places': helper_functions.get_number_of_places(),
                'number_of_users': helper_functions.get_number_of_users()}
    return render_template('index.html', db_infos=db_infos)


@app.route('/ratings/', methods=['POST', 'GET'])
@app.route('/ratings/<count>', methods=['POST', 'GET'])
@app.route('/ratings/<count>/<sug_count>', methods=['POST', 'GET'])
def by_ratings(count=5, sug_count=15):
    """
    Shows Ratings page. When GET, shows a form with a list of restaurants to
    add. When POST, adds an anonym user to the data base with the ratings given
    before and shows the related suggestions

    Args:
        count: The number of diplayed restaurants for the rating form
        sug_count: The maximal number of suggestions

    Request Methods:
        GET, POST

    Urls:
        '/ratings/'
        '/ratings/<count_of_restaurants_to_rate>'
        '/ratings/<count_of_restaurants_to_rate>/<count_of_wanted_suggestions>'

    Return:
        render template 'ratings.html'

    """
    places = None
    suggestions = None
    log = None
    error = None

    if request.method == 'GET':
        places = helper_functions.get_some_places(count)

    if request.method == 'POST':
        # need to parse the counts when request is POST
        count = int(count)
        sug_count = int(sug_count)
        # values of type [ ( place_id, rating ), ... ]
        values = request.form.items()

        # return value of the mongo_handler add_document function
        # log['_id'] holds the id of the new added user
        log = helper_functions.add_ratings_to_db(values)

        try:
            result = helper_functions.get_suggestions_ratings(
                log['_id'])
            suggestions = result[0][:sug_count]
            log.update({'similarity distance method used':result[1]})
    
        except Exception as e:
            error = str(e)
                
    return render_template('ratings.html', places=places,
                           suggestions=suggestions,
                           log=log,
                           error=error,
                           count=count,
                           sug_count=sug_count)


@app.route('/user/', methods=['POST', 'GET'])
@app.route('/user/<sug_count>', methods=['POST', 'GET'])
def by_user_name(sug_count=15):
    """
    Shows user page, dedicated to suggestions by user names. When GET, shows the
    form with the name to enter and 5 randomly picked user names from the data
    base. When POST, outputs the related suggestions.

    Args:
        sug_count: The maximal number of suggestions

    Request Methods:
        GET, POST

    Urls:
        '/user/'
        '/user/<count_of_wanted_suggestions>'

    Return:
        render template 'user.html'

    """

    name = None
    error = None
    suggestions = None
    users = None
    log = None

    if request.method == 'GET':
        users = helper_functions.get_some_user_names()

    if request.method == 'POST':
        sug_count = int(sug_count)
        name = str(request.form['name'])
        name = name.strip()


        
        try:
            log = helper_functions.get_user_reviews(name)
            result = helper_functions.get_suggestions_username(
                name)
            suggestions = result[0][:sug_count]
            log.update({'similarity distance method used':result[1]})
    
        except Exception as e:
            error = str(e)
    
    return render_template('user.html', name=name, suggestions=suggestions,
                           error=error, users=users, log=log,
                           sug_count=sug_count)


if __name__ == '__main__':
    # To run localy
    app.run(debug=True)

    # In order to save time, we decided to run the flask development server
    # online, which is not recommended for real production purposes
    # On the remote server the above line is changed with the following
    # app.run(host='0.0.0.0',port = 80, debug=True)
    # Note that web_client.py has to be run with root rights in that case
