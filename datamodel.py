# datamodel.py
# Created by Hugh Macready (hugh@macready.id.au)
# Data model to be used is NDB for Google App Engine
#
# Data Model Overview
# -------------------
# User
# Waypoint
# Vessel
# TODO List
#     Subtype various properties and write _validate methods
#       Write DirectionProperty which takes 'ENE' etc

from google.appengine.ext import ndb

# User (child=Vessel)     TODO
#     EmailAddress*
#     Password
#     FirstName
#     LastName
#     SubscribedTo (Vessel)*
#     FacebookPage     TODO
#     TwitterPage     TODO

class User(ndb.Model):
    pass

# Vessel (parent=User)
#     Name
#     Flag     TODO (ndb.FlagProperty() ?)
#     HomePort
#     LengthOverAll
#     MaratimeMobileServiceIdentity (MMSI)
#     Callsign     As reported via Airmail / YOTREPS messages
#     satPhoneNumber
#     emergencyContact     TODO
#     publicReportingDelay (Days)     TODO

class Vessel(ndb.Model):
    
    name = ndb.StringProperty()
    callsign = ndb.StringProperty()  #unique
    home_port = ndb.StringProperty()
    length_over_all = ndb.FloatProperty() #in meters
    mmsi = ndb.StringProperty()  #unique
    sat_phone_number = ndb.StringProperty()

class Waypoint(ndb.Model):

    """NDB datastore class for base class waypoint.
    
    This is a base class at this stage not meant to be used directly."""

    vessel = ndb.KeyProperty(kind=Vessel)
    position = ndb.GeoPtProperty(required=True)
    comment = ndb.TextProperty()
    report_date = ndb.DateTimeProperty() 
    received_date = ndb.DateTimeProperty(required=True,auto_now_add=True)
    updated_date = ndb.DateTimeProperty(auto_now=True)
    course = ndb.StringProperty()
    speed = ndb.FloatProperty()
    depth = ndb.FloatProperty()
    
class Weather(ndb.Model):
    
    """ NDB datastore object capturing the weather observation. 
    
    All measurements are in SI units, period in whole seconds, directions in 
    true degrees, speed in kts.
    """
    waypoint = ndb.KeyProperty(kind=Waypoint)
    wind_speed = ndb.FloatProperty()
    wind_direction = ndb.StringProperty()
    wind_waves_height = ndb.FloatProperty()
    wind_waves_period = ndb.IntegerProperty()
    primary_swell_height = ndb.FloatProperty()
    primary_swell_direction = ndb.StringProperty()
    primary_swell_period = ndb.IntegerProperty()
    barometric_pressure = ndb.FloatProperty()
    barometric_pressure_3hr_trend = ndb.FloatProperty()
    cloud_cover_percent = ndb.FloatProperty()
    visibility = ndb.FloatProperty()
    air_temperature = ndb.FloatProperty()
    sea_temperature = ndb.FloatProperty()
    
class GeoPt(ndb.GeoPt):
     
    """Wrapper for GAE GeoPt
    
    Needed in order to maintain client abstraction from google.appengine.ext.ndb 
    """
    pass
    

