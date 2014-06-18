import logging
import datetime
from google.appengine.api.datastore_errors import BadValueError

from google.appengine.ext import ndb
from webapp2 import RequestHandler, WSGIApplication

import datamodel
from geocal.point import Point, InvalidPointError


class WebPositionReport(RequestHandler):

    def __init__(self, request, response):
        RequestHandler.initialize(self, request, response)
        self.fd = self.request.POST
        self.err = {}

    def post(self, vessel_key):
        #Note that login is required in app.yaml, but still check that user is not reporting for another vessel
        user = datamodel.Owner.get_key()
        vessel = ndb.Key(urlsafe=vessel_key)
        if not user == vessel.parent():
            self.response.out.http_status_message(403)
            return

        self.wpt = datamodel.Waypoint(parent=vessel)
        self.add_coords()

        self.wpt.report_date = datetime.datetime.utcnow()
            # if self.fd['speed']:
            #     wpt.speed = float(self.fd['speed'])
            # if self.fd['course']:
            #     wpt.heading = int(self.fd['course'])
            # if self.fd['depth']:
            #     wpt.depth = float(self.fd['depth'])
            # if self.fd['comment']:
            #     wpt.comment = self.fd['comment']
        if not self.err:
            self.wpt.put()
            self.redirect('/myvessel')
        else:
            print self.err
            self.redirect('/myvessel')

    def add_coords(self):
        pt = Point()
        try:
            pt.set_lat(self.fd['latdeg'], self.fd['latmin'])
        except InvalidPointError as point_err:
            self.err['lat'] = str(point_err)
        try:
            pt.set_lon(self.fd['londeg'], self.fd['lonmin'])
        except InvalidPointError as point_err:
            self.err['lon'] = str(point_err)
        self.wpt.position = ndb.GeoPt(pt.lat, pt.lon)


application = WSGIApplication([
    ('/posreport/key/(.+)', WebPositionReport),
    ])