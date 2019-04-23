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

from google.appengine.api import users
from datamodel import Vessel,Waypoint,Weather
import csv
import StringIO
from gpxpy.gpx import GPX, GPXWaypoint
import configdata

__author__ = 'hmacread'

import webapp2
from jinja_env import JINJA_ENV

class DownloadCsv(webapp2.RequestHandler):

    def get(self):
        vessel = Vessel.get_key().get()
        wpt_qry = Waypoint.query(ancestor=vessel.key).order(-Waypoint.report_date, -Waypoint.received_date)
        waypoints = wpt_qry.fetch(configdata.MAX_WAYPOINTS)
        csv_str = StringIO.StringIO()
        fieldnames = ['latitude','longitude','comment','report_date',
                      'received_date','update_date','course','speed','depth']
        writer = csv.DictWriter(csv_str, fieldnames, dialect='excel')
        writer.writeheader()
        for waypoint in waypoints:
            rowDict = {'latitude' : str(waypoint.position.lat),
                'longitude' : str(waypoint.position.lon),
                'report_date' : str(waypoint.report_date),
                'received_date' : str(waypoint.received_date),
                'update_date' : str(waypoint.updated_date),
                'course' : str(waypoint.course),
                'speed' : str(waypoint.speed),
                'depth' : str(waypoint.depth)
                }
            if waypoint.comment:
                rowDict['comment'] = waypoint.comment.encode(encoding="utf-8", errors="ignore")
            writer.writerow(rowDict)
        self.response.write(csv_str.getvalue())

class DownloadGpx(webapp2.RequestHandler):

    def get(self):
        vessel = Vessel.get_key().get()
        wpt_qry = Waypoint.query(ancestor=vessel.key).order(-Waypoint.report_date, -Waypoint.received_date)
        waypoints = wpt_qry.fetch(configdata.MAX_WAYPOINTS)
        gpx = GPX()
        for waypoint in waypoints:
            wpt = GPXWaypoint(waypoint.position.lat, waypoint.position.lon)
            wpt.time = waypoint.received_date
            if waypoint.comment:
                wpt.description = waypoint.comment.encode(encoding="utf-8", errors="ignore")
            gpx.waypoints.append(wpt)
        self.response.write(gpx.to_xml())

application = webapp2.WSGIApplication([('/download.csv', DownloadCsv),
                                        ('/download.gpx', DownloadGpx),
                                        ])
