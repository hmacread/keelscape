# coding=utf-8
__author__ = 'hmacread'

import math
from google.appengine.ext import ndb

class Point():

    def __init__(self, deglat=0, deglon=0, minlat=0, minlon=0):

        """Create a Point object.  From degrees and minutes of latitude and longitude.

        :param deglat: Degrees of lattitude provided as a string, float, or int.  If not a whole number then minlat bust be 0.
        :param deglon: Degrees of longitude provided as a string, float, or int.  If not a whole number then minlon bust be 0.
        :param minlat: 0 if deglat is not whole number.  String, float or int minutes of latitude otherwise.
        :param minlon: 0 if deglon is not whole number.  String, float or int minutes of longitude otherwise.
        """
        self.set_lat(deglat, minlat)
        self.set_lon(deglon, minlon)

    def __str__(self):

        return str(self.lat) + ',' + str(self.lon)

    def set_lat(self, deg=0, min=0):

        if not (-90 <= float(deg) <= 90):
            raise InvalidPointError("%s degrees of latitude not between -90 and 90.")
#        whole_deg, dec_min = math.modf(float(deg))
#        if float(min) != 0 and dec_min != 0:
#            raise InvalidPointError("Decimal degrees as well as minutes supplied.")
        if not (0 <= abs(float(min)) < 60):
            raise InvalidPointError("%s minutes of latitude not less than 60.")

        self.lat = float(deg) + float(min) / 60

    def set_lon(self, deg=0, min=0):

        if not (-180 <= float(deg) <= 180):
            raise InvalidPointError("%s degrees of longitude not between -90 and 90.")

#        whole_deg, dec_min = math.modf(float(deg))
#        if min != 0 and dec_min != 0:
#            raise InvalidPointError("Decimal degrees as well as minutes supplied.")
        if not (0 <= abs(float(min)) < 60):
            raise InvalidPointError("%s minutes of longitude not less than 60.")

        self.lon = float(deg) + float(min) / 60

    def get_ndb_geopt(self):

        return ndb.GeoPt(self.lat, self.lon)

    @staticmethod
    def human_readable(degrees):

        """Takes a float and outputs a human readable deg / decimant minutes. Not Validated."""

        min, deg = math.modf(degrees)
        return str(int(deg)) + u'° ' + str(abs(min * 60)) + '\''

    @staticmethod
    def human_readable_lat(degrees):
        if degrees >= 0:
            return Point.human_readable(abs(degrees)) + ' N'
        else:
            return Point.human_readable(abs(degrees)) + ' S'

    @staticmethod
    def human_readable_lon(degrees):
        if degrees >= 0:
            return Point.human_readable(abs(degrees)) + ' E'
        else:
            return Point.human_readable(abs(degrees)) + ' W'

class InvalidPointError(Exception):

    def __init__(self, msg):

        self.msg = msg

    def __str__(self):

        return ("Invalid Point: " + self.msg)