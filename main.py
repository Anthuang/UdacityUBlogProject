import jinja2
import hashlib
import hmac
import os
import random
import string
import webapp2
from google.appengine.ext import db

template_dir = os.path.join(os.path.dirname(__file__), 'templates')
jinja_env = jinja2.Environment(loader = jinja2.FileSystemLoader(template_dir), autoescape = True)

file = open('secret.txt', 'r')
secret = file.read()

class BlogPosts(db.Model):
    title = db.StringProperty(required = True)
    body = db.TextProperty(required = True)
    owner = db.StringProperty(required = True)
    likes = db.IntegerProperty(required = True)
    created = db.DateTimeProperty(auto_now_add = True)

class Comments(db.Model):
    body = db.TextProperty(required = True)
    owner = db.StringProperty(required = True)
    created = db.DateTimeProperty(auto_now_add = True)

class Likes(db.Model):
    owner = db.StringProperty(required = True)

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

class Blog(Handler):
    def get(self):
        if self.user:
            entries = BlogPosts.all().order('-created')
            self.render('blog.html', entries=entries, name=self.user.username)
        else:
            self.redirect('login')

class Login(Handler):
    def get(self):
        if self.user:
            self.redirect('/')
        else:
            self.render('login.html')

    def post(self):
        username = self.request.get('username')
        password = self.request.get('password')

        if username and password:
            user = Users.all().filter('username', username).get()
            if user:
                if Users.check_pw(username, password, user.password):
                    self.gen_cookie(user.key().id())
                    self.redirect('/')
                else:
                    error = 'Wrong password!'
                    self.render('login.html', error=error)
            else:
                error = 'Nonexistent username!'
                self.render('login.html', error=error)
        else:
            error = 'Fill all fields!'
            self.render('login.html', error=error)

class Signup(Handler):
    def get(self):
        self.render('signup.html')

    def post(self):
        username = self.request.get('username')
        password = self.request.get('password')
        verify = self.request.get('verify')

        if (username and password and verify) and (password == verify):
            user = Users.all().filter('username', username).get()
            if user:
                error = 'Username exists!'
                self.render('signup.html', error=error)
            else:
                new_user = Users(username=username, password=Users.gen_db_password(username, password))
                new_user.put()
                self.gen_cookie(new_user.key().id())
                self.redirect('/')
        else:
            error = 'Something went wrong!'
            self.render('signup.html', error=error)

class Logout(Handler):
    def get(self):
        self.gen_cookie('')
        self.redirect('/login')

class NewPost(Handler):
    def get(self):
        if self.user:
            self.render('newpost.html')
        else:
            self.redirect('/login')

    def post(self):
        subject = self.request.get('subject')
        content = self.request.get('content')

        if subject and content:
            entry = BlogPosts(title=subject, body=content, owner=self.user.username, likes=0)
            entry.put()
            self.redirect('/newpost/' + str(entry.key().id()))
        else:
            self.render('newpost.html', error='Please fill out both fields!')

class NewPostID(Handler):
    def get(self, post_id):
        if self.user:
            post = BlogPosts.get_by_id(int(post_id))
            if not post:
                self.error(404)
                return
            comments = Comments.all().ancestor(post).order('created')
            liked = Likes.all().ancestor(post).filter('owner', self.user.username).get()
            if liked:
                self.render('blogpost.html', entry=post, comments=comments, liked=True)
            else:
                self.render('blogpost.html', entry=post, comments=comments, liked=False)
        else:
            self.render('/login')

class Edit(Handler):
    def get(self, post_id):
        if self.user:
            post = BlogPosts.get_by_id(int(post_id))
            if not post:
                self.error(404)
                return
            if self.user.username == post.owner:
                self.render('editpost.html', entry=post, can_edit=True)
            else:
                error = 'You cannot change posts you do not own'
                self.render('editpost.html', entry=post, can_edit=False, error=error)
        else:
            self.redirect('/login')

    def post(self, post_id):
        subject = self.request.get('subject')
        content = self.request.get('content')

        if subject and content:
            post = BlogPosts.get_by_id(int(post_id))
            post.title = subject
            post.body = content
            post.put()
            self.redirect('/newpost/' + str(post.key().id()))
        else:
            self.render('editpost.html', error='Please fill out both fields!')

class Delete(Handler):
    def get(self, post_id):
        if self.user:
            post = BlogPosts.get_by_id(int(post_id))
            if not post:
                self.error(404)
                return
            if self.user.username == post.owner:
                post.delete()
                self.redirect('/')
            else:
                error = 'You cannot change posts you do not own'
                self.render('editpost.html', entry=post, can_edit=False, error=error)
        else:
            self.redirect('/login')

class Like(Handler):
    def get(self, post_id):
        if self.user:
            post = BlogPosts.get_by_id(int(post_id))
            if not post:
                self.error(404)
                return
            if self.user.username != post.owner:
                liked = Likes.all().ancestor(post).filter('owner', self.user.username).get()
                if not liked:
                    new_like = Likes(owner=self.user.username, parent=post)
                    new_like.put()
                    post.likes += 1
                    post.put()
                    self.redirect('/newpost/' + str(post.key().id()))
                else:
                    self.redirect('/newpost/' + str(post.key().id()))
            else:
                error = 'You cannot like your own post'
                self.render('editpost.html', entry=post, can_edit=False, error=error)
        else:
            self.redirect('/login')

class Comment(Handler):
    def post(self, post_id):
        content = self.request.get('content')
        post = BlogPosts.get_by_id(int(post_id))
        if not post:
            self.error(404)
            return
        if self.user:
            if content:
                comment = Comments(body=content, owner=self.user.username, parent=post)
                comment.put()
                self.redirect('/newpost/' + post_id)
            else:
                self.render('blogpost.html', entry=post, error='Cannot submit an empty comment')
        else:
            self.redirect('/login')

app = webapp2.WSGIApplication([
    ('/', Blog), ('/login', Login), ('/signup', Signup), ('/logout', Logout),
    ('/newpost', NewPost), ('/newpost/(\d+)', NewPostID),
    ('/edit/(\d+)', Edit), ('/delete/(\d+)', Delete),
    ('/like/(\d+)', Like), ('/newcomment/(\d+)', Comment)
], debug=True)
