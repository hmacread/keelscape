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


__author__ = 'hmacread'

import webapp2
from jinja_env import JINJA_ENV

class DownloadCsv(webapp2.RequestHandler):

    MAX_WAYPOINTS = 10000

    def get(self):

        vessel = Vessel.get_key().get()
        wpt_qry = Waypoint.query(ancestor=vessel.key).order(-Waypoint.report_date, -Waypoint.received_date)
        waypoints = wpt_qry.fetch(self.MAX_WAYPOINTS)
        csv = "latitude,longitude,comment,report_date,recived_date,update_date,course,speed,depth\n"
        for waypoint in waypoints:
            csv += str(waypoint.position.lat) + ","
            csv += str(waypoint.position.lat) + ","
            csv += "\"" + str(waypoint.comment) + "\","
            csv += str(waypoint.report_date) + ","
            csv += str(waypoint.received_date) + ","
            csv += str(waypoint.updated_date) + ","
            csv += str(waypoint.course) + ","
            csv += str(waypoint.speed) + ","
            csv += str(waypoint.depth) + "\n"

        self.response.write(csv)

application = webapp2.WSGIApplication([('/download.csv', DownloadCsv),])
