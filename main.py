from handlers import *

app = webapp2.WSGIApplication([
    ('/', Blog), ('/login', Login), ('/signup', Signup), ('/logout', Logout),
    ('/newpost', NewPost), ('/newpost/(\d+)', NewPostID),
    ('/edit/(\d+)', Edit), ('/delete/(\d+)', Delete),
    ('/like/(\d+)', Like), ('/newcomment/(\d+)', Comment),
    ('/deletecomment/(\d+)', DeleteComment), ('/editcomment/(\d+)', EditComment)
], debug=True)
