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

from google.appengine.ext import ndb
from webapp2 import RequestHandler, WSGIApplication
from datamodel import Owner

__author__ = 'hmacread'

class WptDeleteRequest(RequestHandler):

    def post(self, wpt_key_str):
        wpt_key = ndb.Key(urlsafe=wpt_key_str)
        this_owner = Owner.get_key()
        #assumes that wpts are only children of vessels that are in turn children of owners
        wpt_owner = wpt_key.parent().parent()

        if this_owner == wpt_owner:
            wpt_key.delete()
            self.redirect(self.request.POST['redirect_url'])
        else:
            self.response.out.http_status_message(403)

application = WSGIApplication([
    ('/waypoint/delete/(.+)', WptDeleteRequest),
    ])
