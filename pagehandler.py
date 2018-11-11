""" Copyright 2018 Hugh Macready

Licensed under the Apache License, Version 2.0 (the "License");
you may not use this file except in compliance with the License.
You may obtain a copy of the License at

    http://www.apache.org/licenses/LICENSE-2.0

Unless required by applicable law or agreed to in writing, software
distributed under the License is distributed on an "AS IS" BASIS,
WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
See the License for the specific language governing permissions and
limitations under the License.
"""

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