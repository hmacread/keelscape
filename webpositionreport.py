import logging
import datetime
from google.appengine.api.datastore_errors import BadValueError

import webapp2
from google.appengine.ext import ndb
from google.appengine.api import users

import datamodel


class WebPositionReport(webapp2.RequestHandler):

    """Supports post only"""
    
    def post(self, vessel_key):
        #Note that login is required in app.yaml
        user = users.get_current_user()
        val = self.request.POST
        wpt = datamodel.Waypoint(parent=ndb.Key(urlsafe=vessel_key))
        try:
            lat = int(val['latdeg']) + float(val['latmin']) / 60
            lon = int(val['londeg']) + float(val['lonmin']) / 60
            wpt.position = ndb.GeoPt(lat,lon)
            wpt.report_date = datetime.datetime.utcnow()
            if val['speed']:
                wpt.speed = float(val['speed'])
            if val['course']:
                wpt.heading = int(val['course'])
            if val['depth']:
                wpt.depth = float(val['depth'])
            if val['comment']:
                wpt.comment = val['comment']
            wpt.put()
        except (ValueError,BadValueError):
            logging.info("Bad Value Entered.")
            #TODO create messaging for bad values / highlighting

        self.redirect('/myvessel')


application = webapp2.WSGIApplication([
    ('/posreport/key/(.+)', WebPositionReport),
    ])