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

import webapp2
from google.appengine.ext import ndb

__author__ = 'hmacread'

from jinja_env import JINJA_ENV
from datamodel import *

class WeatherAtWaypoint(webapp2.RequestHandler):

    def get_template_params(self, waypoint_key):
        waypoint = waypoint_key.get()
        weather = Weather.query(Weather.waypoint == waypoint_key).get()
        return {
                'loginurl': users.create_login_url('/'),
                'waypoint': waypoint,
                'weather': weather,
                }

    def get(self, waypoint_key_str):
        template = JINJA_ENV.get_template('weather.html')
        waypoint_key = ndb.Key(urlsafe=waypoint_key_str)
        params = self.get_template_params(waypoint_key)
        self.response.write(template.render(params))

application = webapp2.WSGIApplication([('/weather/waypoint/(.+)', WeatherAtWaypoint),])
