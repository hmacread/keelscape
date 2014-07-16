# coding=utf-8
__author__ = 'hmacread'

import math

class Point():

    def __init__(self, deglat=0, deglon=0, minlat=0, minlon=0):

        """Create a Point object.  From degrees and minutes of latitude and longitude.

        :param deglat: Degrees of lattitude provided as a string, float, or int.  If not a whole number then minlat bust be 0.
        :param deglon: Degrees of longitude provided as a string, float, or int.  If not a whole number then minlon bust be 0.
        :param minlat: 0 if deglat is not whole number.  String, float or int minutes of latitude otherwise.  If deglat is non-zero then it's sign must match.
        :param minlon: 0 if deglon is not whole number.  String, float or int minutes of longitude otherwise.  If deglon is non-zero then it's sign must match.
        """
        self.set_lat(deglat, minlat)
        self.set_lon(deglon, minlon)

    def __str__(self):

        return str(self.lat) + ',' + str(self.lon)

    def set_lat(self, deg=0, min=0, dir=None):

        """Validates the parameters and sets the longitude.

        :param deg:  Degree as described in constructor.
        :param min:  Minutes as described in constructor.
        :param dir:  If provided overrides the sign of deg and min.  Valid strings 'N' & 'S'.
        """
        deg = float(deg)
        min = float(min)
        if dir:
            if str(dir) == 'N':
                pass
            elif str(dir) == 'S':
                deg *= -1
                min *= -1
            else:
                raise InvalidPointError("Invalid direction provided, must be 'N' or 'S'")

        self.check_coordinate(True, deg, min)
        self.lat = float(deg) + float(min) / 60

    def set_lon(self, deg=0, min=0, dir=None):

        """Validates the parameters and sets the longitude.

        :param deg:  Degree as described in constructor.
        :param min:  Minutes as described in constructor.
        :param dir:  If provided overrides the sign of deg and min. Valid strings 'N' & 'S'.
        """
        deg = float(deg)
        min = float(min)
        if dir:
            if str(dir) == 'E':
                pass
            elif str(dir) == 'W':
                deg *= -1
                min *= -1
            else:
                raise InvalidPointError("Invalid direction provided, must be 'E' or 'W'")

        self.check_coordinate(False, deg, min)
        self.lon = deg + min / 60

    @staticmethod
    def check_coordinate(type, deg=0, min=0):

        """Checks that either a lat or lon is valid.

        :param type: True if lattitude to be checked, false if longitude.
        :param deg: Number of whole or decimal degrees to be checked.
        :param min: Number of minutes in to be checked.  Only valid if deg is a whole number.
        :raise InvalidPointError: Raised if given coordinate is invalid.
        """
        try:
            deg = float(deg)
            min = float(min)
        except ValueError:
            raise InvalidPointError("Invalid value given for degree and or minute.")
        if type:
            lim = 90
        else:
            lim = 180
        if not deg * min >= 0:
            raise InvalidPointError("Minutes sign does not match degrees.")
        dec_min, whole_deg = math.modf(float(deg))
        if float(min) != 0 and dec_min != 0:
            raise InvalidPointError("Decimal degrees as well as minutes supplied.")
        if not (0 <= abs(min) < 60):
            raise InvalidPointError("%s minutes not less than 60." % min)
        if not (0 <= abs(deg) + abs(min) / 60 < lim):
            raise InvalidPointError("%s degrees and %s min not between -%s and %s." % (deg, min, lim ,lim))


    @staticmethod
    def human_readable(degrees):

        """Takes a float and outputs a human readable deg / decimant minutes. Not Validated."""
        min, deg = math.modf(degrees)
        return str(int(deg)) + u'° ' + str(abs(round(min * 60, 3))) + '\''

    @staticmethod
    def human_readable_lat(degree):
        if degree >= 0:
            return Point.human_readable(abs(degree)) + ' N'
        else:
            return Point.human_readable(abs(degree)) + ' S'

    @staticmethod
    def human_readable_lon(degree):
        if degree >= 0:
            return Point.human_readable(abs(degree)) + ' E'
        else:
            return Point.human_readable(abs(degree)) + ' W'

    @property
    def dirlat(self):
        if self.lat >= 0:
            return 'N'
        else:
            return 'S'

    @property
    def dirlon(self):
        if self.lon >= 0:
            return 'E'
        else:
            return 'W'

    @property
    def latdeg(self):
        _, deg = math.modf(self.lat)
        return abs(int(deg))

    @property
    def latmin(self):
        min, _ = math.modf(self.lat)
        return abs(min * 60)

    @property
    def londeg(self):
        _, deg = math.modf(self.lon)
        return abs(int(deg))

    @property
    def lonmin(self):
        min, _ = math.modf(self.lon)
        return abs(min * 60)

    @property
    def lat_str(self):
        return self.human_readable_lat(self.lat)

    @property
    def lon_str(self):
        return self.human_readable_lat(self.lon)


class InvalidPointError(Exception):

    def __init__(self, msg):
        self.msg = msg

    def __str__(self):
        return ("Invalid Point: " + self.msg)

if __name__ == '__main__':
    import tests.point_test
    tests.point_test.main()