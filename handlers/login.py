from utils import *
from models.users import *

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