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
        
        
class VesselList(webapp2.RequestHandler):
    
    def get(self):

        vessel_query = datamodel.Vessel.query()
        vessels = vessel_query.fetch(20)

        template = JINJA_ENV.get_template('vessellist.html')
        self.response.write(template.render(vessels=vessels))
        
class Vessel(webapp2.RequestHandler):
    
    def get(self, vessel_id): 
        
        vessel = datamodel.Vessel.get_by_id(vessel_id)
        
        template = JINJA_ENV.get_template('vessel.html')
        self.response.write(template.render())
         
        
        
application = webapp2.WSGIApplication([
    ('/', LandingPage),
    ('/vessel', VesselList),
    ('/vessel/(\d+)', Vessel),
    ], debug=True)