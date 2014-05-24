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
    def exists(cls, user=None, email=None):
        """Test for existence of a user.

        :param email: use to check for vessels with that email address.
        :param user: user paramenter, if unspecified current user will be queried.
        :return: non-zero if the Owner exists.
        """
        if not user:
            user = users.get_current_user()
        return Owner.query(Owner.id == user.user_id()).count(limit=1)


    @classmethod
    def get_key(cls, user=None):
        """Return a key to an Owner object.

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
    loa = ndb.FloatProperty() #in meters
    draft = ndb.FloatProperty() #in meters
    callsign = ndb.StringProperty(validator=validate_callsign)  #unique

    @classmethod
    def exists(cls, owner_key=None, email=None, callsign=None):
        if callsign:
            return Vessel.query(Vessel.callsign == callsign).count(limit=1)
        if email:
            return Vessel.query(Vessel.email == email).count(limit=1)
        if not owner_key:
            owner_key = Owner.get_key(users.get_current_user())
        return Vessel.query(ancestor=owner_key).count(limit=1)

    @classmethod
    def get_key(cls, owner_key=None):
        if not owner_key:
            owner_key = Owner.get_key(users.get_current_user())
        return Vessel.query(ancestor=owner_key).get(keys_only=True)

    @classmethod
    def get(cls, owner_key=None):
        return Vessel.get_key(owner_key).get()


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
