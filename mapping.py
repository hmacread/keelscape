from google.appengine.ext import ndb
from geocal.point import Point
import datamodel

__author__ = 'hmacread'

from configdata import GOOGLE_API_KEY

class Map():

    def render(self):
        pass

class GoogleMap(Map):

    DEFAULT_ZOOM = 8
    API_KEY = GOOGLE_API_KEY
    WORLD_ZOOM = 2

    def __init__(self):
        self.centre = Point()
        self.zoom = self.DEFAULT_ZOOM
        self.type = "HYBRID"



class GoogleMapCurrentLocation(GoogleMap):

    DEFAULT_ZOOM = 5

    def __init__(self, vessel):
        GoogleMap.__init__(self)
        self.current_wpt = datamodel.Waypoint.query(ancestor=vessel.key).order(-datamodel.Waypoint.report_date).get()
        self.centre = self.current_wpt.position

    def vessel_location(self):
        return self.current_wpt.position

class GoogleMapTrack(GoogleMap):

    DEFAULT_ZOOM = 4
    MAX_WPTS = 500

    def __init__(self, vessel):
        GoogleMap.__init__(self)
        self.wpts = datamodel.Waypoint.query(ancestor=vessel.key).order(datamodel.Waypoint.report_date).fetch(500)
        if self.wpts:
            self.current_wpt = self.wpts.pop()
            self.centre = self.current_wpt.position
        else:
            self.current_wpt = None
            self.zoom = self.WORLD_ZOOM
            self.centre = ndb.GeoPt(0,0)

    def vessel_location(self):
        if self.current_wpt:
            return self.current_wpt.position
        else:
            return None

    def last_report(self):
        if self.current_wpt:
            return str(self.current_wpt.report_date)
        else:
            return None