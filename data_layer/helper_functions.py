from mongo_handler import YelpMongoHandler
import datetime



def add_ratings_to_db(values):

    front_handler = YelpMongoHandler('frontend_users')
    places_handler = YelpMongoHandler('places')

    user = {}
    reviews = []

    for v in values:
        place = places_handler.get_documents(one = True, query = {'_id' : v[0]} )
        review={}
        review['place_id']=place['_id']
        review['place_name']=place['name']
        review['rating'] = v[1]
        reviews.append(review)

    user['reviews'] = reviews
    user['name'] = "anonym"
    
    #BETTER SOLUTION??
    user['_id'] = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    _return = front_handler.add_document( user )

    return _return


def get_places():
    
    places_handler = YelpMongoHandler('places')

    return places_handler.get_documents()

        
def get_suggestions_ratings(_id):

    front_handler = YelpMongoHandler('frontend_users')
    user = front_handler.get_documents(one=True, query={'_id' : _id})
    
    return [user]

def get_suggestions_username(name):
    
    user_handler = YelpMongoHandler('users_info')
    #Hopefully no users with same name because then it would be with id
    user =  user_handler.get_documents(one=True, query={'name' : name}) 
    print user
    print name
    if not user:
        return None
    return [ user ]
