import jinja2
import hashlib
import hmac
import os
import random
import string
import webapp2

from models.users import Users

file = open('secret.txt', 'r')
secret = file.read()

template_dir = os.path.join(os.path.dirname(__file__), 'templates')
jinja_env = jinja2.Environment(loader = jinja2.FileSystemLoader(template_dir), autoescape = True)

class Handler(webapp2.RequestHandler):
    def write(self, *a, **kw):
        self.response.out.write(*a, **kw)

    def render_str(self, template, **params):
        t = jinja_env.get_template(template)
        return t.render(params)

    def render(self, template, **kw):
        self.write(self.render_str(template, **kw))

    def gen_cookie(self, user_id):
        if user_id:
            user_hash = hmac.new(secret, str(user_id)).hexdigest()
            cookie = 'user_id=%s; Path=/' % (str(user_id) + '|' + user_hash)
        else:
            cookie = 'user_id=; Path=/'
        self.response.headers.add_header('Set-Cookie', cookie)

    def check_cookie(self):
        msg = self.request.cookies.get('user_id')
        if msg:
            user_id = msg.split('|')[0]
            user_hash = msg.split('|')[1]
            check_hash = hmac.new(secret, user_id).hexdigest()
            if user_hash == check_hash:
                return Users.get_by_id(int(user_id))
        else:
            return None

    def initialize(self, *a, **kw):
        webapp2.RequestHandler.initialize(self, *a, **kw)
        self.user = self.check_cookie()

def login_required(func):
    """
    A decorator to confirm a user is logged in or redirect as needed.
    """
    def login(self, *args, **kwargs):
        # Redirect to login if user not logged in, else execute func.
        if not self.user:
            self.redirect("/login")
        else:
            func(self, *args, **kwargs)
    return login