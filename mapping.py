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
from geocal.point import Point
import datamodel
import configdata

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
        self.current_wpt = datamodel.Waypoint.query(ancestor=vessel.key).order(-datamodel.Waypoint.report_date,
                                                                               -datamodel.Waypoint.received_date
                                                                              ).get()
        self.centre = self.current_wpt.position

    def vessel_location(self):
        return self.current_wpt.position

class GoogleMapTrack(GoogleMap):

    DEFAULT_ZOOM = 4

    def __init__(self, vessel):
        GoogleMap.__init__(self)
        self.wpts = datamodel.Waypoint.query(ancestor=vessel.key).order(datamodel.Waypoint.report_date,
                                                                        datamodel.Waypoint.received_date
                                                                        ).fetch(configdata.MAX_WAYPOINTS)
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
