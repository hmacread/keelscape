from google.appengine.ext import ndb
from webapp2 import RequestHandler, WSGIApplication
from datamodel import Owner

__author__ = 'hmacread'

class WptDeleteRequest(RequestHandler):

    def delete(self, wpt_key_str):
        wpt_key = ndb.Key(urlsafe=wpt_key_str)
        this_owner = Owner.get_key()
        #assumes that wpts are only children of vessels that are in turn children of owners
        wpt_owner = wpt_key.parent().parent()

        if this_owner == wpt_owner:
            wpt_key.delete()
            self.redirect('/myvessel')
        else:
            self.response.out.http_status_message(403)

application = WSGIApplication([
    ('/waypoint/delete/(.+)', WptDeleteRequest),
    ])