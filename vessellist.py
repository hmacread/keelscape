from google.appengine.api import users
from datamodel import Vessel

__author__ = 'hmacread'

import webapp2
from jinja_env import JINJA_ENV

class VesselList(webapp2.RequestHandler):

    def get_template_params(self):

        vessels = Vessel.query().fetch(100)
        return {
                'loginurl': users.create_login_url('/'),
                'vessels': vessels
                }

    def get(self):
        template = JINJA_ENV.get_template('vessellist.html')
        params = self.get_template_params()
        self.response.write(template.render(params))

application = webapp2.WSGIApplication([('/vessellist', VesselList),])