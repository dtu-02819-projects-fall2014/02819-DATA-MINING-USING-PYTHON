import mongo_handler
import recommendations
import datetime
import functools

handler = mongo_handler.YelpMongoHandler()

def add_ratings_to_db(values):

    user = {}
    reviews = []

    for v in values:
        place = handler.get_documents('places', one = True, query = {'_id' : v[0]} )
        review={}
        review['_id'] = place['_id']
        review['name'] = place['name']
        review['rating'] = float(v[1])
        reviews.append(review)

    user['reviews'] = reviews
    user['name'] = "anonym"
    
    #BETTER SOLUTION??
    user['_id'] = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S.%f")[:-3]

    _return = handler.add_document( user, 'frontend_users')

    return _return


def get_places():
    
    return handler.get_documents('places')

        
def get_suggestions_ratings(_id):


    user = handler.get_documents('frontend_users',one=True, query={'_id' : _id})
    
    return _suggestions(user)


def get_suggestions_username(name):
    

    #Hopefully no users with same name because then it would be with id
    user =  handler.get_documents('users_info',one=True, query={'name' : name}) 

    if not user:
        raise NameError("No user found with the name %s"%(name))

    return _suggestions(user)

def _suggestions(user):

    users = handler.get_documents('users_info') + handler.get_documents('frontend_users')
   
    prefs = {}
    for user in users:
        prefs.update( _transform_for_suggestions(user))
    
    reco_ids = recommendations.getRecommendations(prefs , user['_id'])
    
    suggestions=[]
    for score, place_id in reco_ids:
        place = handler.get_documents('places', one = True, query = {'_id' : place_id })
        place['score'] = score
        suggestions.append( place )
    return suggestions

def _transform_for_suggestions( user ):
    
    ratings={}
    for r in user['reviews']:
        ratings[r['_id']] = r['rating']
    return { user['_id'] : ratings }
