from HTMLParser import HTMLParser
import datetime
from google.appengine.api.datastore_errors import BadValueError
from google.appengine.datastore.datastore_query import Cursor

from webapp2 import WSGIApplication, RequestHandler

from datamodel import *
from jinja_env import JINJA_ENV

from geocal.point import Point, InvalidPointError
import configdata
from mapping import GoogleMapTrack

__author__ = 'hmacread'

class VesselPage(RequestHandler):

    NUM_WAYPOINTS = 5

    def get_template_params(self, vessel_key):
        self.vessel_key = vessel_key
        vessel = vessel_key.get()

        wpt_qry = Waypoint.query(ancestor=vessel.key).order(-Waypoint.report_date, -Waypoint.received_date)
        curs = Cursor(urlsafe=self.request.get('cursor'))
        params = {'loginurl': users.create_login_url('/'),
                'vessel': vessel,
                'map' : GoogleMapTrack(vessel)
                }
        if self.request.get('cursor'):
            params['start_url'] = self.get_base_url()
            params['cursor'] = self.request.get('cursor')
        else:
            params['start_url'] = ''
        params['waypoints'], next_curs, params['older'] = wpt_qry.fetch_page(self.NUM_WAYPOINTS, start_cursor=curs)
        if params['older'] and next_curs:
            params['next_page_url'] = self.get_base_url() + "?cursor=" + next_curs.urlsafe()
        else:
            params['older'] = False

        # #Formulate reverse pointer if there is more recent waypoints
        # rev_wpt_qry = Waypoint.query(ancestor=vessel.key).order(Waypoint.report_date, Waypoint.received_date)
        # rev_curs = curs.reversed()
        # _, prev_curs, params['newer'] = wpt_qry.fetch_page(self.NUM_WAYPOINTS, start_cursor=rev_curs)
        # if params['newer'] and prev_curs:
        #      params['prev_page_url'] = self.get_base_url() + "?cursor=" + prev_curs.reversed().urlsafe()
        # else:
        #      params['newer'] = False


        return params

    def get_base_url(self):
        return "/vessel/key/" + self.vessel_key.urlsafe()

    def get(self, vessel_key_str):
        template = JINJA_ENV.get_template('vessel.html')
        vessel_key = ndb.Key(urlsafe=vessel_key_str)
        params = self.get_template_params(vessel_key)
        self.response.write(template.render(params))


class MyVesselPage(VesselPage):

    NUM_WAYPOINTS = 10

    def get_template_params(self, vessel_key):
        #call for basic vessel parameters
        params = VesselPage.get_template_params(self, vessel_key)
        #add myvessel specific data
        params.update({'user': users.get_current_user(),
                       'public_link': '/vessel/key/' + vessel_key.urlsafe(),
                       'submit_wpt_url': '/posreport/key/' + vessel_key.urlsafe(),
                       'logouturl': users.create_logout_url('/'),
                       })
        return params

    #Authentication enforced by app.yaml
    def get(self, form_errs=None, form_content=None):
        if not Vessel.exists():
            #owner got here without creating a vessel somehow
            self.redirect('/newvessel')
        else:
            vessel_key = Vessel.get_key()
            params = self.get_template_params(vessel_key)
            params['report_date'] = datetime.datetime.utcnow().strftime('%Y-%m-%d %H:%M')
            if form_content:
                params.update(form_content)
            if form_errs:
                params['errors'] = form_errs
            template = JINJA_ENV.get_template('myvessel.html')
            self.response.write(template.render(params))

    def get_base_url(self):
        return '/myvessel'

class WebPositionReport(MyVesselPage):

    def __init__(self, request, response):
        RequestHandler.initialize(self, request, response)
        self.fd = self.request.POST
        self.err = {}

    def post(self, vessel_key):
        #Note that login is required in app.yaml, but still check that user is not reporting for another vessel
        user = Owner.get_key()
        vessel = ndb.Key(urlsafe=vessel_key)
        if not user == vessel.parent():
            self.response.out.http_status_message(403)
            return
        self.wpt = Waypoint(parent=vessel)
        self.add_all()
        if not self.err:
            self.wpt.put()
            self.redirect('/myvessel')
        else:
            self.get(self.err, self.request.POST)

    def add_all(self):
        self.add_coords()
        self.add_date()
        self.add_depth()
        self.add_speed()
        self.add_course()
        self.add_comment()

    def add_coords(self):
        pt = Point()
        try:
            if not self.fd['latmin']:
                self.fd['latmin'] = 0
            pt.set_lat(self.fd['latdeg'], self.fd['latmin'], self.fd['dirlat'])
        except (InvalidPointError, ValueError) as point_err:
            self.err['lat'] = str(point_err)
        try:
            if not self.fd['lonmin']:
                self.fd['lonmin'] = 0
            pt.set_lon(self.fd['londeg'], self.fd['lonmin'], self.fd['dirlon'])
        except (InvalidPointError, ValueError) as point_err:
            self.err['lon'] = str(point_err)
        self.wpt.position = ndb.GeoPt(pt.lat, pt.lon)

    def add_date(self):
        try:
            dt = datetime.datetime.strptime(self.fd['report_date'], '%Y-%m-%d %H:%M')
            self.wpt.report_date = dt
        except (ValueError, AssertionError) as error:
            self.err['report_date'] = str(error)

    def add_speed(self):
        try:
            if self.fd['speed']:
                speed = float(self.fd['speed'])
                assert 0.0 <= speed <= 50.0
                self.wpt.speed = float(speed)
        except (ValueError, TypeError, BadValueError, AssertionError):
            self.err['speed'] = "You may enter a speed between 0.0 and 50.0 kts."

    def add_course(self):
        try:
            if self.fd['course']:
                course = int(self.fd['course'])
                assert 0 <= course < 360
                self.wpt.course = str(course)
        except (ValueError, TypeError, BadValueError, AssertionError):
            self.err['course'] = "You may enter a course between 0 and 359 degrees."


    def add_depth(self):
        try:
            if self.fd['depth']:
                depth = float(self.fd['depth'])
                assert 0.0 <= depth <= 50000.0
                self.wpt.depth = float(depth)
        except (ValueError, TypeError, BadValueError, AssertionError):
            self.err['depth'] = "You may enter a depth between 0.0 and 50000.0 m."

    def add_comment(self):
        try:
            self.wpt.comment = strip_tags(self.fd['comment'])
        except BadValueError:
            self.err['comment'] = "Invalid comment."


class MLStripper(HTMLParser):
    def __init__(self):
        self.reset()
        self.fed = []
    def handle_data(self, d):
        self.fed.append(d)
    def get_data(self):
        return ''.join(self.fed)

def strip_tags(html):
    s = MLStripper()
    s.feed(html)
    return s.get_data()

application = WSGIApplication([('/myvessel', MyVesselPage),
                               ('/vessel/key/(.+)', VesselPage),
                               ('/posreport/key/(.+)', WebPositionReport),

                               ])
