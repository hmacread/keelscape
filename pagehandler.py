import logging
import webapp2
import urllib
import os

from google.appengine.ext import ndb
from google.appengine.api import users
from jinja2 import Environment, FileSystemLoader

import datamodel

#Jinja Environment instanciation to be used.
JINJA_ENV = Environment(
     loader=FileSystemLoader(os.path.dirname(__file__) + '/templates'),
     extensions=['jinja2.ext.autoescape'],
     autoescape=True
     )

class Landing(webapp2.RequestHandler):

    def get(self):
        user = users.get_current_user()        
        if user:
            #User is authenticated
            owner_qry = datamodel.Owner.query(datamodel.Owner.id == user.user_id())
            if not owner_qry.count():
                #User is not an Owner in DB, add them
                owner = datamodel.Owner(id=user.user_id(),
                                        email=user.email(),
                                        nickname=user.nickname(),
                                        )
                owner_key = owner.put()
            else:
                #User is an owner in DB, get their key
                owner_key = owner_qry.get(keys_only=True)
                
            if datamodel.Vessel.query(ancestor=owner_key).count():
                #Owner has a vessel, view it
                self.redirect('/myvessel')
            else:
                #Owner does not have a vessel, send to create form
                self.redirect('/newvessel')
                
        else:
            #redirect to splash
            template = JINJA_ENV.get_template('splash.html')
            self.response.write(template.render(
                                        loginurl=users.create_login_url('/')
                                        ))    

class MyVessel(webapp2.RequestHandler):
    
    NUM_WAYPOINTS = 10
    
    #Authentication enforced by app.yaml
    def get(self):
        user = users.get_current_user()
        vessel = get_vessel(user=user)
        if not vessel:
            #owner got here without creating a vessel somehow
            logging.info('got here')
            self.redirect('/newvessel') 
        
        wpt_qry = datamodel.Waypoint.query(ancestor=vessel.key).order(
                                                datamodel.Waypoint.report_date)
                                        
        
        template = JINJA_ENV.get_template('myvessel.html')
        params = {
            'user' : user,
            'vessel' : vessel,
            'pulic_link' : '/vessel/key/' + vessel.key.urlsafe(),
            'submit_wpt_url' : '/posreport/key/' + vessel.key.urlsafe(),
            'logouturl' : users.create_logout_url('/'),
            'waypoints' :  wpt_qry.fetch(self.NUM_WAYPOINTS),
        }
            
        self.response.write(template.render(params))
                                        
class NewVessel(webapp2.RequestHandler):
    
    def get(self):

        user = users.get_current_user()    
        vessel = get_vessel(user=user)
        template = template = JINJA_ENV.get_template('newvessel.html')
        self.response.write(template.render(
                                        vessel=vessel,
                                        user=user,
                                        logouturl=users.create_logout_url('/')
                                        ))
    
    def post(self):
        #Note that login is required in app.yaml
        user = users.get_current_user()    
        owner_key = get_owner_key(user)
        vessel_qry = datamodel.Vessel.query(ancestor=owner_key)
        if vessel_qry.count():
            #editing existing vessel
            vessel = datamodel.Vessel.query(ancestor=owner_key).get()
        else:
            vessel = datamodel.Vessel(parent=owner_key)
            
        values = self.request.POST
        vessel.owner_id = user.user_id()
        vessel.name = values['name']
        vessel.home_port = values['home_port']
        vessel.flag = values['flag']
        #need to type check
        if values['length_over_all']:
            vessel.length_over_all = float(values['length_over_all'])
        if values['draft']:
            vessel.draft = float(values['draft'])
        #need to check if these are unique
        vessel.callsign = values['callsign']
        vessel.mmsi = values['mmsi']
        
        vessel.put()
        self.redirect('/myvessel')

class Vessel(webapp2.RequestHandler):
    
    NUM_WAYPOINTS = 5
    
    def get(self, vessel_key): 
        
        vessel = ndb.Key(urlsafe=vessel_key).get()
        template = JINJA_ENV.get_template('vessel.html')
        wpt_qry = datamodel.Waypoint.query(ancestor=vessel.key).order(
                                                datamodel.Waypoint.report_date)
                                                
        self.response.write(template.render(loginurl=users.create_login_url('/'),
                                            vessel=vessel,
                                            waypoints=wpt_qry.fetch(self.NUM_WAYPOINTS),
                                            ))
                                            
        
class VesselMap(webapp2.RequestHandler):

    def get(self, vessel_key):
        
        vessel = vessel_key.get()
        template = JINJA_ENV.get_template('vesselmap.html')
        self.response.write(template.render(vessel=vessel))

#Some DB helper methods

def get_owner_key(user):
    #Find a way to save this query by generating a Key directly from owner_id
    owner = datamodel.Owner.query(datamodel.Owner.id == user.user_id())
    return owner.get(keys_only=True)

def has_vessel(user):

    return datamodel.Vessel.query(ancestor=get_owner_key(user)).count()

def get_vessel(user):

    return datamodel.Vessel.query(ancestor=get_owner_key(user)).get()

def get_vessel_key(user):

    return datamodel.Vessel.query(ancestor=get_owner_key(user)).get(keys_only=True)
     
           
application = webapp2.WSGIApplication([
    ('/', Landing),
    ('/myvessel', MyVessel), 
    ('/newvessel', NewVessel),
    ('/editvessel', NewVessel),
    ('/vessel/key/(.+)', Vessel),
    ('/vessel/map/(\d+)', VesselMap),
    ], debug=True)