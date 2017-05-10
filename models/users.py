from utils import *
from google.appengine.ext import db

class Users(db.Model):
    username = db.StringProperty(required = True)
    password = db.StringProperty(required = True)

    @classmethod
    def gen_db_password(cls, name, pw):
        salt = ''.join(random.choice(string.letters) for n in range(5))
        hashed_pw = hashlib.sha256(name + pw + salt).hexdigest()
        return hashed_pw + ',' + salt

    @classmethod
    def check_pw(cls, name, pw, db_pw):
        hashed_pw = db_pw.split(',')[0]
        salt = db_pw.split(',')[1]
        if hashed_pw == hashlib.sha256(name + pw + salt).hexdigest():
            return True
        return False