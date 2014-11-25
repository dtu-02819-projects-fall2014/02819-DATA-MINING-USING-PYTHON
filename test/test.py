import os
import urllib2
import os

url_path = os.path.abspath('yelp_user_test_page.html')
test_url = 'file://{}'.format(url_path)
local_test_url = urllib2.urlopen(test_url).read()

def test():
    assert 4 == 4
