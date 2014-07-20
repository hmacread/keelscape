# positionreport.py
# Created by Hugh Macready (hugh@macready.id.au)
# defines a class representing a YOTREPS position report

import logging
import datetime

from datamodel import *
from google.appengine.ext import ndb

class PositionReport():

        
    def __init__(self, line_iterator):
    
        """Takes parses the iterator over enumerated sequence of line strings"""
        self.weather = None
        #Skip to AIRMAIL header
        for num, line in line_iterator:
            line = line.strip()
            if not line.find('AIRMAIL') == -1:
                break
        else:
            raise PositionReportError(0,"<Empty body>")

        if 'YOTREPS' in line:
            self.parse_yotrep(line_iterator)
        else:
            raise PositionReportError(num,line)
    
    def put_contents(self):        
        
        """Writes out required new DB objects and updates relationships
        
        TODO move to PositionReport and make ancestor?)"""
        wpt_key =  self.waypoint.put()
        if self.weather:
            self.weather.waypoint = wpt_key
            self.weather.put()
        

    def parse_yotrep(self, lines_iterator):

        SAILMAIL_FOOTER_DIV='-------------------------------------------------'
    
        logging.info("Parsing content of message as YOTREP.")        
        for num, line in lines_iterator:
            type, seperator, data = line.partition(':')
            #skip all lines after sailmail footer divider
            if line.strip() == SAILMAIL_FOOTER_DIV:
                break
            #skip lines without semi-colon or data
            if not (seperator and data.strip()):
                continue
            try:
                self.write_yotrep_field(type.strip(), data.strip())
            except (AssertionError, TypeError, ValueError):
               raise PositionReportError(num,line)
        
        
            
    def write_yotrep_field(self, type, data):   
        """Maps each field to a waypoint,vessel ndb object property
        
        Note: Order is important for LATITUDE and LONGITUDE, IDENT must be first.
              MARINE : YES must precede weather.  
        """
        
        if type == 'IDENT':
            qry = Vessel.query(Vessel.callsign == data.upper())
            vessel_key = qry.get(keys_only=True)
            if not vessel_key:
                raise VesselNotFoundError(data)
            self.waypoint = Waypoint(parent=vessel_key)
        elif type == 'TIME':
            self.waypoint.report_date = self.parse_yotreps_date(data)        
        elif type == 'LATITUDE': 
            self.waypoint.position = ndb.GeoPt(self.parse_yotreps_lat(data),0)
        elif type == 'LONGITUDE':
            self.waypoint.position = ndb.GeoPt(self.waypoint.position.lat,
                                               self.parse_yotreps_lon(data))
        elif type == 'COURSE':
            self.waypoint.course = data
        elif type == 'SPEED':
            self.waypoint.speed = float(data)
        elif type == 'MARINE':
            self.weather = Weather()
        elif type == 'WIND_DIR':
            self.weather.wind_direction = data
        elif type == 'WIND_SPEED':
            self.weather.wind_speed = float(data)
        elif type == 'WAVE_HT':
            self.weather.wind_waves_height = float(data.strip('M'))
        elif type == 'WAVE_PER' or type == 'WAVE_PD':
            self.weather.wind_waves_period = int(data)
        elif type == 'SWELL_DIR':
            self.weather.primary_swell_direction = data
        elif type == 'SWELL_HT':
            self.weather.primary_swell_height = float(data.strip('M'))
        elif type == 'SWELL_PER' or type == 'SWELL_PD':
            self.weather.primary_swell_period = int(data)
        elif type == 'CLOUDS':
            self.weather.cloud_cover_percent = float(data.strip('%')) / 100.0
        elif type == 'VIS' or type == 'VISIBILITY':  
            self.weather.visibility = float(data)
        elif type == 'BARO':
            self.weather.barometric_pressure = float(data)
        elif type == 'TREND':
            self.weather.barometric_pressure_3hr_trend = float(data)
        elif type == 'AIR_TEMP':
            self.weather.air_temperature = float(data.strip('C'))
        elif type == 'SEA_TEMP':
            self.weather.sea_temperature = float(data.strip('C'))
        elif type == 'COMMENTS' or type == 'COMMENT':
            self.waypoint.comment = data
        else:
            logging.warning("Unsupport data type received: %s: %s" % (type, data)) 

    @staticmethod
    def parse_yotreps_date(data):
        
        """Parse time of form '2014/05/10 01:15'"""
        
        date, time = data.split(' ', 1)
        year, month, day = date.split('/',2)
        hour, minute = time.split(':')
        return datetime.datetime(int(year), 
                                 int(month), 
                                 int(day),
                                 int(hour), 
                                 int(minute))
    
    @staticmethod
    def parse_yotreps_lat(data):
        
        """Parse lat in the form '02-49.80N'
        
        Note: Decimal minutes is not limited in accuracy to 2 decimal places"""
        
        degrees, min_dir = data.split('-', 1)
        direction = min_dir[len(min_dir) - 1]
        minutes = min_dir.rstrip('NS')
        idegrees = int(degrees)
        if '-' in minutes:
            iminutes, iseconds = minutes.split('-', 1)
            assert 0 <= float(iseconds) < 60
            fminutes = float(iminutes) + float(iseconds) / 60
        else:
            fminutes = float(minutes)

        assert 0 <= fminutes < 60
        fdegrees = idegrees + fminutes / 60
        if direction == 'S':
            fdegrees *= -1
        assert -90 <= fdegrees <= 90
        return fdegrees

    @staticmethod
    def parse_yotreps_lon(data):
        
        """Parse lon in the form '143-49.80W'
        
        Note: Decimal minutes is NOT limited in accuracy to 2 decimal places
              -180.0 longitude is illegal instead use 180.0 """
        
        degrees, min_dir = data.split('-', 1)
        direction = min_dir[len(min_dir) - 1]
        minutes = min_dir.rstrip('EW')
        idegrees = int(degrees)
        if '-' in minutes:
            iminutes, iseconds = minutes.split('-', 1)
            assert 0 <= float(iseconds) < 60
            fminutes = float(iminutes) + float(iseconds) / 60
        else:
            fminutes = float(minutes)
        assert 0 <= fminutes < 60
        fdegrees = idegrees + fminutes / 60
        if direction == 'W':
            fdegrees *= -1
        assert -180 < fdegrees <= 180
        return fdegrees
                                         
class PositionReportError(Exception):

    """Raised when an error is encountered parsing an position at line_number"""

    def __init__(self, line_number, line):

        self.line_number = line_number
        self.line = line

    def __str__(self):

        return ("Error in email position report on line %s,\n%s" % 
                                (str(self.line_number), self.line))

class VesselNotFoundError(Exception):

    """Position report received for a vessel not registered previously"""

    def __init__(self, callsign):

        self.callsign = callsign

    def __str__(self):

        return ("Error in email position report: Vessel %s not found." % 
                                                            self.callsign)
                                                                