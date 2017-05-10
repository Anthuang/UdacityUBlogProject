from google.appengine.ext import db

class BlogPosts(db.Model):
    title = db.StringProperty(required = True)
    body = db.TextProperty(required = True)
    owner = db.StringProperty(required = True)
    likes = db.IntegerProperty(required = True)
    created = db.DateTimeProperty(auto_now_add = True)