######DTU - Technical University of Denmark
##Project for course: 02819 Data mining with Python
##### Config file
Inorder to use the configure_yelp_api.py and the populate_mongo.py files, you have to add a config file called conf.ini in the root of the project.

This file should follow this template:
```
[Tokens]
CONSUMER_KEY = <input key>
CONSUMER_SECRET = <input key>
TOKEN = <input key>
TOKEN_SECRET = <input key>
```

##### Test
The test suit can be run **from** the test folder by calling the nose framwork:
```
nosetests -v
```

