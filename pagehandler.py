import logging
import webapp2
import urllib
import datetime
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

class LandingPage(webapp2.RequestHandler):

    def get(self):
        user = users.get_current_user()
        if user:
            #user is logged in with OpenID / Google Accounts
            mms_user = datamodel.User.query(datamodel.User.user == user).get()
            if mms_user:
                # We've seen this user before send them to landing page
                logging.info('user_id ' + user.user_id() + ' already seen')
                template = JINJA_ENV.get_template('landing.html')
                self.response.write(template.render(
                                            mms_user=mms_user,
                                            navbar=get_nav_bar()
                                            ))
            else: 
                # New MMS user, put into the DB and redirect to accounts page
                logging.info("user_id: " + user.user_id() + " not seen, creating")
                new_user = datamodel.User()
                
                new_user.user = user
                #new_user.user_id = long(user.user_id())
                #new_user.name = user.nickname()
                #new_user.email_address = user.email()       
                new_user.put()
                self.redirect('/account')
                
        else:
            #redirect to OpenID Auth page / URL
            template = JINJA_ENV.get_template('splash.html')
            self.response.write(template.render(
                                        loginurl=users.create_login_url('/')
                                        ))
        
        
class VesselList(webapp2.RequestHandler):
    
    def get(self):

        vessel_query = datamodel.Vessel.query()
        vessels = vessel_query.fetch(20)

        template = JINJA_ENV.get_template('vessellist.html')
        self.response.write(template.render(navbar=get_nav_bar(),
                                            vessels=vessels))
        
class Vessel(webapp2.RequestHandler):
    
    def get(self, vessel_id): 
        
        vessel = datamodel.Vessel.get_by_id(vessel_id)
        
        template = JINJA_ENV.get_template('vessel.html')
        self.response.write(template.render(navbar=get_nav_bar()))        

class Tracking(webapp2.RequestHandler):

    def get(self):

        template = JINJA_ENV.get_template('tracking.html')
        self.response.write(template.render(navbar=get_nav_bar()))        

        
class About(webapp2.RequestHandler):

    def get(self):

        template = JINJA_ENV.get_template('about.html')
        self.response.write(template.render(navbar=get_nav_bar()))        

class Account(webapp2.RequestHandler):

    def get(self):

       #TODO
        user = users.get_current_user()
        mms_user = datamodel.User.query(datamodel.User.user == user).get()
        vessel = datamodel.Vessel.query(ancestor=mms_user.key).fetch()
        
        template = JINJA_ENV.get_template('account.html')
        self.response.write(template.render(navbar=get_nav_bar(),
                                            mms_user=mms_user,
                                            vessel=vessel,
                                            ))        
        
                
def get_nav_bar():
    
    """ Returns a list of href, caption tuples for use in the navigation bar """
    
    return [('Home', '/'),
            ('Tracking','/tracking'),
            ("Who's out there?",'/vessel'),
            ('About','/about'),
            ('Account',"/account"),
            ('Logout',users.create_logout_url('/')),
           ]
           
application = webapp2.WSGIApplication([
    ('/', LandingPage),
    ('/vessel', VesselList),
    ('/vessel/(\d+)', Vessel),
    ('/about', About),
    ('/account', Account)
    ], debug=True)