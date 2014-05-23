import logging
import webapp2
import os

from google.appengine.ext import ndb
from google.appengine.ext.db import BadValueError
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


class Vessel(webapp2.RequestHandler):

    NUM_WAYPOINTS = 5
    GMAPS_EMBED_API_KEY = "AIzaSyBMhILdBdcbYKlKzYg3WeiMfO_Y0tFd-XM"

    def get_template_params(self, vessel_key):
        vessel = vessel_key.get()
        wpt_qry = datamodel.Waypoint.query(ancestor=vessel.key).order(-datamodel.Waypoint.report_date)

        map_url = ("https://www.google.com/maps/embed/v1/place" +
                   "?key=" + self.GMAPS_EMBED_API_KEY +
                   "&q=" + str(wpt_qry.get().position) +
                   "&zoom=5" +
                   "&maptype=satellite"
                   )

        return {'loginurl': users.create_login_url('/'),
                'vessel': vessel,
                'waypoints': wpt_qry.fetch(self.NUM_WAYPOINTS),
                'map_url': map_url
                }

    def get(self, vessel_key_str):
        template = JINJA_ENV.get_template('vessel.html')
        vessel_key = ndb.Key(urlsafe=vessel_key_str)
        self.response.write(template.render(self.get_template_params(vessel_key)))


class MyVessel(Vessel):

    NUM_WAYPOINTS = 10

    def get_template_params(self, vessel_key, user):
        #call super class
        params = Vessel.get_template_params(self, vessel_key)
        #add myvessel specific data
        params.update({'user': user,
                       'pulic_link': '/vessel/key/' + vessel_key.urlsafe(),
                       'submit_wpt_url': '/posreport/key/' + vessel_key.urlsafe(),
                       'logouturl': users.create_logout_url('/'),
                       })
        return params

    #Authentication enforced by app.yaml
    def get(self):
        user = users.get_current_user()
        vessel_key = get_vessel_key(user)
        if not vessel_key:
            #owner got here without creating a vessel somehow
            self.redirect('/newvessel')
        template = JINJA_ENV.get_template('myvessel.html')
        self.response.write(template.render(self.get_template_params(vessel_key, user)))

class NewVesselError(Exception):
    def __init__(self, msg):
        self.msg = msg
    def __str__(self):
        return self.msg


class NewVessel(webapp2.RequestHandler):

    def get(self):

        user = users.get_current_user()
        vessel = get_vessel(user)
        template = JINJA_ENV.get_template('newvessel.html')
        self.response.write(template.render(
            vessel=vessel,
            user=user,
            logouturl=users.create_logout_url('/'),
            errormsg='',
        ))

    def put_values(self, vessel):

        data = self.request.POST

        #check name and email exist
        if not data['name']:
            raise NewVesselError('Please enter an vessel name.')
        self.vessel.name = data['name']
        if not data['email']:
            raise NewVesselError('Please enter an email address.')

        #check uniqueness of email or callsign
        if datamodel.Vessel.query(datamodel.Vessel.callsign == data['email']).count():
            raise NewVesselError('Sorry ' + data['email'] + ' is already in use.')
        if data['callsign'] and datamodel.Vessel.query(datamodel.Vessel.callsign == data['callsign']).count():
            raise NewVesselError('The callsign ' + data['callsign'] + ' is already in use.')



        self.vessel.put()
        logging.info('got here')

    def post(self):

        user = users.get_current_user()
        self.vessel = datamodel.Vessel(parent=get_owner_key(user))
        try:
            self.put_values(self.vessel)
            self.redirect('/myvessel')
        except NewVesselError as error:
            template = template = JINJA_ENV.get_template('newvessel.html')
            self.response.write(template.render(
                vessel=self.vessel,
                user=user,
                logouturl=users.create_logout_url('/'),
                errormsg=str(error)
                ))




# class VesselMap(webapp2.RequestHandler):
#
#     def get(self, vessel_key):
#
#         vessel = vessel_key.get()
#         template = JINJA_ENV.get_template('vesselmap.html')
#         self.response.write(template.render(vessel=vessel))

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
                                          ('/vessel/key/(.+)', Vessel),
                                          ('/newvessel', NewVessel),
                                          #('/editvessel', NewVessel),
                                          #('/vessel/map/(\d+)', VesselMap),
                                      ], debug=True)