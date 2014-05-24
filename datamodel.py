# datamodel.py
# Created by Hugh Macready (hugh@macready.id.au)
# Data model to be used is NDB for Google App Engine
#
from google.appengine.api import users
from google.appengine.ext import ndb

from geocal.point import Point

class Owner(ndb.Model):

    """Represents an owner of a vessel."""

    id = ndb.StringProperty()
    email = ndb.StringProperty()
    nickname = ndb.StringProperty()

    @classmethod
    def exists(cls, user=None):
        if not user:
            user = users.get_current_user()
        return Owner.query(Owner.id == user.user_id()).count(limit=1)


    @classmethod
    def get_key(cls, user=None):
        """
        Return a key to an Owner object.

        :param user: Optional google user object, if not specified then current user is called.
        :return: ndb.Key for specified user, or current user if None.
        """
        if not user:
            user = users.get_current_user()
        return Owner.query(Owner.id == user.user_id()).get(keys_only=True)

    @classmethod
    def get(cls, user=None):
        return Owner.get_key(user).get()


def validate_callsign(property, value):

    value = value.strip()
    return value

class Vessel(ndb.Model):
    
    """Represents an MMS vessel"""

    name = ndb.StringProperty()
    email = ndb.StringProperty()
    home_port = ndb.StringProperty()
    flag = ndb.StringProperty()
    length_over_all = ndb.FloatProperty() #in meters
    draft = ndb.FloatProperty() #in meters
    callsign = ndb.StringProperty(validator=validate_callsign)  #unique

    @classmethod
    def exists(cls, user=None):
        if not user:
            user = users.get_current_user()
        return Vessel.query(ancestor=Owner.get_key(user)).count()


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
