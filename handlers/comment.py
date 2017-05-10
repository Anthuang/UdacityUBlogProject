from utils import *
from models.blogposts import *
from models.comments import *

class Comment(Handler):
    @login_required
    def post(self, post_id):
        content = self.request.get('content')
        post = BlogPosts.get_by_id(int(post_id))
        if not post:
            self.error(404)
            return
        if content:
            comment = Comments(post=post, owner=self.user.username, body=content)
            comment.put()
            self.redirect('/newpost/' + post_id)
        else:
            self.render('blogpost.html', entry=post, error='Cannot submit an empty comment')

class DeleteComment(Handler):
    @login_required
    def get(self, comment_id):
        comment = Comments.get_by_id(int(comment_id))
        if not comment:
            self.error(404)
            return
        if self.user.username == comment.owner:
            comment.delete()
            self.redirect('/newpost/' + str(comment.post.key().id()))
        else:
            error = 'You cannot delete comments you do not own'
            self.render('editpost.html', entry=comment, can_edit=False, error=error)

class EditComment(Handler):
    @login_required
    def get(self, comment_id):
        comment = Comments.get_by_id(int(comment_id))
        if not comment:
            self.error(404)
            return
        if self.user.username == comment.owner:
            self.render('editcomment.html', comment=comment)
        else:
            error = 'You cannot change posts you do not own'
            self.render('editpost.html', entry=comment.post, can_edit=False, error=error)

    @login_required
    def post(self, comment_id):
        content = self.request.get('content')

        if content:
            comment = Comments.get_by_id(int(comment_id))
            if not comment:
                self.error(404)
                return
            if self.user.username != comment.owner:
                error = 'You cannot change comments you do not own'
                self.render('editpost.html', entry=comment.post, can_edit=False, error=error)
            comment.body = content
            comment.put()
            self.redirect('/newpost/' + str(comment.post.key().id()))
        else:
            self.render('editcomment.html', error='Please fill out both fields!')