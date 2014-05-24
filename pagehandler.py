from webapp2 import WSGIApplication, RequestHandler
from jinja_env import JINJA_ENV
from datamodel import *

class LandingPage(RequestHandler):
    def get(self):
        user = users.get_current_user()
        if user:
            #User is authenticated
            if not Owner.exists(user):
                #User is not an Owner in DB, add them
                owner = Owner(id=user.user_id(),
                              email=user.email(),
                              nickname=user.nickname(),
                              )
                owner_key = owner.put()
            else:
                #User is an owner in DB, get their key
                owner_key = Owner.get_key(user)

            if Vessel.exists(owner_key):
                #Owner has a vessel, view it
                self.redirect('/myvessel')
            else:
                #Owner does not have a vessel, send to create form
                self.redirect('/newvessel')
        else:
            #redirect to splash
            template = JINJA_ENV.get_template('splash.html')
            self.response.write(template.render(
                loginurl=users.create_login_url('/')
            ))

application = WSGIApplication([('/', LandingPage)])