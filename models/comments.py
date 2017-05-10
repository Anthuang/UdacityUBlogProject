from google.appengine.ext import db
from models.blogposts import *

class Comments(db.Model):
    post = db.ReferenceProperty(BlogPosts, collection_name='comments')
    owner = db.StringProperty(required = True)
    body = db.TextProperty(required = True)
    created = db.DateTimeProperty(auto_now_add = True)