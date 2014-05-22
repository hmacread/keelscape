# datamodel.py
# Created by Hugh Macready (hugh@macready.id.au)
# Data model to be used is NDB for Google App Engine
#
from google.appengine.ext import ndb

from geocal.point import Point


class Owner(ndb.Model):

    """Represents an owner of a vessel."""

    id = ndb.StringProperty()
    email = ndb.StringProperty()
    nickname = ndb.StringProperty()


class Vessel(ndb.Model):
    
    """Represents an MMS vessel"""

    name = ndb.StringProperty()
    home_port = ndb.StringProperty()
    flag = ndb.StringProperty()
    length_over_all = ndb.FloatProperty() #in meters
    draft = ndb.FloatProperty() #in meters
    callsign = ndb.StringProperty()  #unique
    mmsi = ndb.StringProperty()  #unique


class Waypoint(ndb.Model):

    """NDB datastore class for base class waypoint."""

    position = ndb.GeoPtProperty(required=True)
    comment = ndb.TextProperty()
    report_date = ndb.DateTimeProperty() 
    received_date = ndb.DateTimeProperty(required=True,auto_now_add=True)
    updated_date = ndb.DateTimeProperty(auto_now=True)
    course = ndb.StringProperty()
    speed = ndb.FloatProperty()
    depth = ndb.FloatProperty()

    @property
    def human_readable_lat(self):
        return Point.human_readable_lat(self.position.lat)

    @property
    def human_readable_lon(self):
        return Point.human_readable_lon(self.position.lon)


class Weather(ndb.Model):
    
    """ NDB datastore object capturing the weather observation. 
    
    All measurements are in SI units, period in whole seconds, directions in 
    true degrees, speed in kts.
    """
    
    waypoint = ndb.KeyProperty(kind='Waypoint')
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
