from utils import *
from models.blogposts import *
from models.likes import *

class Blog(Handler):
    def get(self):
        if self.user:
            entries = BlogPosts.all().order('-created')
            self.render('blog.html', entries=entries, name=self.user.username)
        else:
            self.redirect('login')

class NewPost(Handler):
    def get(self):
        if self.user:
            self.render('newpost.html')
        else:
            self.redirect('/login')

    def post(self):
        if self.user:
            subject = self.request.get('subject')
            content = self.request.get('content')

            if subject and content:
                entry = BlogPosts(title=subject, body=content, owner=self.user.username, likes=0)
                entry.put()
                self.redirect('/newpost/' + str(entry.key().id()))
            else:
                self.render('newpost.html', error='Please fill out both fields!')
        else:
            self.redirect('/login')

class NewPostID(Handler):
    def get(self, post_id):
        if self.user:
            post = BlogPosts.get_by_id(int(post_id))
            if not post:
                self.error(404)
                return
            comments = post.comments.order('created')
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
        if self.user:
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
        else:
            self.redirect('/login')

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