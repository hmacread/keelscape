# coding=utf-8
__author__ = 'hmacread'
from geocal.point import *

#TODO Convert to Python unittest framework

class Tests():

    @staticmethod
    def origin_point():
        return (Point().lat == 0 and Point().lon == 0)

    @staticmethod
    def decimal_degree_only():
        x = Point()
        x.set_lat(43.2)
        x.set_lon(165.231234212)
        return (x.lat == 43.2) and (x.lon == 165.231234212)

    @staticmethod
    def minute_lat():
        x = Point()
        x.set_lat(0, 15)
        return x.lat == 0.25

    @staticmethod
    def minute_lon():
        x = Point()
        x.set_lat(25, 15)
        return x.lat == 25.25

    @staticmethod
    def dec_degrees_and_minutes_error():
        x = Point()
        try:
            x.set_lat(20.25, 12.12)
            return False
        except InvalidPointError:
            return True

    @staticmethod
    def human_readables():
        passed = True
        x = Point()
        x.set_lat(12.1)
        if not x.lat_str == u'12° 6.0\' N':
            passed = False
        x.set_lat(12, 32.666666666666666)
        if not x.lat_str == u'12° 32.667\' N':
            passed = False
        x.set_lon(12.1)
        if not x.lon_str == u'12° 6.0\' N':
            passed = False
        x.set_lon(12, 32.666666666666666)
        if not x.lon_str == u'12° 32.667\' N':
            passed = False
        return passed

    @staticmethod
    def limit_tests():
        x = Point()
        passed = True
        try:
            x.set_lat(89.99999999)
            if not x.lat == 89.99999999: passed = False
        except InvalidPointError:
            passed = False
        return passed

    @staticmethod
    def limit_test_error():
        x = Point()
        passed = True
        lats = [(90, 0.1), (91, 0), (-90, 1), (-40, 60), (-59, 60), (3, 60), (0, 60.000000000001), (40, -12)]
        lons = [(180, 1), (181, 0), (-180.1, 0), (-0, -61), (-160, 1.12)]
        for lat in lats:
            try:
                deg, min = lat
                x.set_lat(deg, min)
                passed = False
            except InvalidPointError:
                pass
        for lon in lons:
            try:
                deg, min = lon
                x.set_lon(deg, min)
                passed = False
            except InvalidPointError:
                pass
        return passed
    
    @staticmethod
    def set_with_direction():
        passed = True
        x = Point()       
        x.set_lat(10, 15, 'N')
        if x.lat != 10.25:
            passed = False
        x.set_lat(10, 15, 'S')
        if x.lat != -10.25:
            passed = False
        x.set_lat(0, 0, 'S')
        if x.lat != 0:
            passed = False
        x.set_lat(0, 15, 'S')
        if x.lat != -0.25:
            passed = False
        x.set_lon(92, 15, 'W')
        if x.lon != -92.25:
            passed = False
        x.set_lon(92, 15, 'E')
        if x.lon != 92.25:
            passed = False
        x.set_lon(0, 0, 'W')
        if x.lon != 0:
            passed = False
        try:
            x.set_lat(1, 2, '-1')
            passed = False
        except InvalidPointError:
            pass
        try:
            x.set_lon(1, 2, 'A wrong strong')
            passed = False
        except InvalidPointError:
            pass
        return passed


def main():

    tests = reversed(dir(Tests))
    for test_name in tests:
        test = getattr(Tests, test_name)
        if callable(test):
            print test_name + ":",
            if test(): print "passed"
            else: print "Failed"


        # if func.__call__
    # if origin_point(): print "passed"
    # else: print "Failed"

    # x = Point(43.2, 23.4)
    # p = p and (x.lat == 43.2 and
    #            x.lon == 23.4)
    # x = Point (0, 0, 0, 0)
    # p = p and (x.lat == 0 and
    #            x.lon == 0)
    # x = Point(0,0,15,15)
    # p = p and (x.lat == 0.25 and
    #            x.lon == 0.25)
    # x = Point(0,0,-15,15)
    # p = p and (x.lat == -0.25 and
    #            x.lon == 0.25)
    # x = Point(0,0,15,-15)
    # p = p and (x.lat == 0.25 and
    #            x.lon == -0.25)
    # x = Point(-20,0,-15,15)
    # p = p and (x.lat == -20.25 and
    #            x.lon == 0.25)
    # x = Point(0,0,15,15)
    # p = p and (x.lat == 0.25 and
    #            x.lon == 0.25)

if __name__ == '__main__':
    main()

