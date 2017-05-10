from google.appengine.ext import db

class Likes(db.Model):
    owner = db.StringProperty(required = True)