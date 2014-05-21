import logging
import datetime

import webapp2
from google.appengine.ext import ndb
from google.appengine.api import users

import datamodel


class WebPositionReport(webapp2.RequestHandler):
    
    def post(self, vessel_key):
        #Note that login is required in app.yaml
        user = users.get_current_user()    
        val = self.request.POST
        lat = int(val['latdeg']) + float(val['latmin']) / 60
        lon = int(val['londeg']) + float(val['lonmin']) / 60
        wpt = datamodel.Waypoint(parent=ndb.Key(urlsafe=vessel_key))
        
        wpt.position = datamodel.GeoPt(lat,lon)
        report_date = datetime.datetime.utcnow()
        if val['speed']:
            wpt.speed = float(val['speed'])
        if val['heading']:
            wpt.heading = int(val['heading'])
        if val['depth']:
            wpt.depth = float(val['depth'])
        if val['comment']:
            wpt.comment = val['comment']
        
        wpt.put()
        self.redirect('/myvessel')
        
application = webapp2.WSGIApplication([
    ('/posreport/key/(.+)', WebPositionReport),
    ], debug=True)