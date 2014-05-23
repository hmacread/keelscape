# coding=utf-8
__author__ = 'hmacread'

import math
from google.appengine.ext import ndb

class Point():

    def __init__(self, ndb_geopt):

        if isinstance(ndb.GeoPt, ndb_geopt):
            self.lat = ndb_geopt.lat
            self.lon = ndb_geopt.lon
        else:
            raise TypeError()

    def __init__(self, deglat, deglon, minlat=0, minlon=0):

        self.lat = float(deglat) + float(minlat) / 60
        self.lon = float(deglon) + float(minlon) / 60

    def __str__(self):

        return str(self.lat) + ',' + str(self.lon)

    def get_ndb_geopt(self):

        return ndb.GeoPt(self.lat, self.lon)

    # TODO proivide humar readable methods for Point
    # def get_human_readable_lat(self):
    #
    #     return self.human_readable(self.lat)
    #
    # def get_human_readable_lon(self):
    #
    #     return self.human_readable(self.lon)

    @staticmethod
    def human_readable(degrees):

        """Takes a float and outputs a human readable deg / decimant minutes. Not Validated."""

        min, deg = math.modf(degrees)
        return str(deg) + u'° ' + str(abs(min * 60)) + '\''

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

