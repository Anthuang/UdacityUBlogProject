from utils import *
from models.blogposts import *
from models.likes import *

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