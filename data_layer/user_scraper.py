import urllib2
from bs4 import BeautifulSoup
import re
from time import sleep
from random import uniform

def soup_reviews(user_id,page_start):
    url= 'http://www.yelp.com/user_details_reviews_self?userid=%s&rec_pagestart=%d'%(user_id,page_start)
    content=urllib2.urlopen(url).read()
    return BeautifulSoup(content)


def soup_friends(user_id):
    friends_url = 'http://www.yelp.com/user_details_friends?userid=%s'%(user_id)
    content=urllib2.urlopen(friends_url).read()
    return BeautifulSoup(content)

def sleep_rand():
      a=uniform(0.20,1)
      print "sleeping %.2f seconds" %(a)
      sleep(a)

def get_user(user_id,length=140):

    page_start=0
    reviews=[]

    #Getting the reviews
    print 'getting reviews..'
    while True:
        print 'scrapping reviews from page %d' %(page_start/10)
        soup=soup_reviews(user_id,page_start)
        for a in soup.find_all('div',class_='review clearfix'):
            r = {}
            r['place'] = {}
            rep={'\n':' ','St':'St ','Ave': 'Ave ','Broadway': 'Broadway ', 'Blvd': 'Blvd ','Rd': 'Rd '}
            r['place']['address'] = replace_all(a.find('address',class_ = 'smaller').get_text().strip(),rep)
            r['place']['url'] = 'http://www.yelp.com'+a.find('a').get('href').split('?hrid')[0]
            r['place']['id'] = a.find('a').get('href').split('=')[1].replace('\n','')
            r['place']['name'] = a.find('a').get_text().replace('\n','').strip()
            r['place']['categories'] = [c.get_text('href').replace('\n','').strip() for c in a.find('p').find_all('a')]
            r['rating'] = float(a.find('div',class_='rating').find('i').get('title')[:3].strip())
            r['created_at'] = a.find(class_='smaller date').get_text().replace('\n','').strip()
            r['text'] = a.find('div',class_='review_comment').get_text().strip().replace('\n','')
            if len(r['text']) >length :
                r['text']=r['text'][:length]+'...'
            reviews.append(r)
            sleep_rand()
        if len(soup.find_all('td',class_='nav-links')) <2:
            break
        page_start+=10
        sleep_rand()

    print 'getting user informations..'
    user={}
    user['id']=user_id
    user['reviews_count']=len(reviews)
    user['reviews']=reviews

    rep={'\n':'','\'s Profile':''}
    user['name']= replace_all(soup.find('div',class_='about-connections').find('h1').get_text(),rep).strip()

    s=soup.find('div',id='about_user_column')

    user['location']=s.find('div',id='profile_questions').find_all('p')[0].get_text().replace('\n','').strip()
    user['created_at']=s.find('div',id='profile_questions').find_all('p')[1].get_text().replace('\n','').strip()

    review_votes=s.find('p',class_='i-review-votes-user_social-wrap').get_text()
    if review_votes != None:
        rv={}
        digits=map(int,re.findall('\d+',review_votes))
        rv['useful'],rv['funny'],rv['cool']=digits[:3]
        rv['total']=sum(digits)
    else:
        rv['useful'],rv['funny'],rv['cool'],rv['total']=0
    user['review_votes']=rv

    soup2=soup_friends(user_id)
    friends=[]
    for f in soup2.find_all('div',class_='friend_box'):
        friend={}
        friend['name']=f.find(class_='user-name').get_text().replace('\n','')
        friend['id']=f.find('a').get('href').split('=')[1].replace('\n','')
        friend['location']=f.find(class_='user-location').get_text().replace('\n','')
        friends.append(friend)
    user['friends']=friends
    user['friends_count']=len(friends)

    return user


def replace_all(text, dic):
    for i, j in dic.iteritems():
        text = text.replace(i, j)
    return text
