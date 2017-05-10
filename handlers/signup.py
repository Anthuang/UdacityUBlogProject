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