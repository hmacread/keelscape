import logging
import webapp2
import urllib
import datetime
import os

from google.appengine.ext import ndb
from jinja2 import Environment, FileSystemLoader

import datamodel

#Jinja Environment instanciation to be used.
JINJA_ENV = Environment(
     loader=FileSystemLoader(os.path.dirname(__file__) + '/templates'),
     extensions=['jinja2.ext.autoescape'],
     autoescape=True
     )



class LandingPage(webapp2.RequestHandler):

    def get(self):
    
        template = JINJA_ENV.get_template('index.html')
        self.response.write(template.render())
        
        logging.debug("GET request for %s completed." % self)
        
class Waypoint(webapp2.RequestHandler):

    def get(self):
        self.response.write(HEADER)
        self.response.write('<h1>Current Waypoints:</h1><br>')
        waypoint_query = datamodel.Waypoint.query().order(
                                            datamodel.Waypoint.received_date)
        waypoints = waypoint_query.fetch(20)

        for waypoint in waypoints:
            self.response.write(str(waypoint.received_date) + '<br>') 

        self.response.write(FOOTER)
        logging.debug("GET request for %s completed." % self)
        
        
class Vessel(webapp2.RequestHandler):
    
    def get(self):
        self.response.write(HEADER)
        self.response.write('<h1>Current Vessel Names:</h1><br>')
        vessel_query = datamodel.Vessel.query()
        vessels = vessel_query.fetch(20)

        for vessel in vessels:
            self.response.write(vessel.callsign + '<br>') 

        self.response.write(FOOTER)
        logging.debug("GET request for %s completed." % self)
        
class Weather(webapp2.RequestHandler):
    
    def get(self):
        self.response.write(HEADER)
        self.response.write('<h1>Current Weather Reports for Waypoints:</h1><br>')
        weather_query = datamodel.Weather.query()
        weather_reps = weather_query.fetch(20)

        for weather in weather_reps:
            self.response.write("%skts at waypoint ID %s <br>" % 
                                        (str(weather.wind_speed),
                                         str(weather.waypoint.id))
                                ) 

        self.response.write(FOOTER)
        logging.debug("GET request for %s completed." % self)
        
application = webapp2.WSGIApplication([
    ('/', LandingPage),
    ('/waypoint', Waypoint),
    ('/vessel', Vessel),
    ('/weather', Weather)
    ], debug=True)