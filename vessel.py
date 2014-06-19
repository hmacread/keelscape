import datetime

__author__ = 'hmacread'

from webapp2 import WSGIApplication, RequestHandler

from datamodel import *
from jinja_env import JINJA_ENV

from geocal.point import Point, InvalidPointError
import configdata


class VesselPage(RequestHandler):

    NUM_WAYPOINTS = 5

    @staticmethod
    def map_url(q=None, zoom=1, maptype="satellite"):

        url = "https://www.google.com/maps/embed/v1/"
        if q:
            return (url + "place" +
                    "?key=" + configdata.GMAPS_EMBED_API_KEY +
                    "&q=" + q +
                    "&zoom=" + str(zoom) +
                    "&maptype=" + maptype
                    )
        else:
            return (url + "view" +
                    "?key=" + configdata.GMAPS_EMBED_API_KEY +
                    "&center=0,%200" +
                    "&zoom=" + str(zoom) +
                    "&maptype=" + maptype
                    )

    def get_template_params(self, vessel_key):
        vessel = vessel_key.get()
        wpt_qry = Waypoint.query(ancestor=vessel.key).order(-Waypoint.report_date)
        if wpt_qry.count(limit=1):
            map_url = self.map_url(q=str(wpt_qry.get().position), zoom=5)
        else:
            map_url = self.map_url()

        return {'loginurl': users.create_login_url('/'),
                'vessel': vessel,
                'waypoints': wpt_qry.fetch(self.NUM_WAYPOINTS),
                'map_url': map_url
                }

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
            if form_content:
                params.update(form_content)
            if form_errs:
                params['errors'] = form_errs
            template = JINJA_ENV.get_template('myvessel.html')
            self.response.write(template.render(params))

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
        self.add_coords()

        self.wpt.report_date = datetime.datetime.utcnow()
            # if self.fd['speed']:
            #     wpt.speed = float(self.fd['speed'])
            # if self.fd['course']:
            #     wpt.heading = int(self.fd['course'])
            # if self.fd['depth']:
            #     wpt.depth = float(self.fd['depth'])
            # if self.fd['comment']:
            #     wpt.comment = self.fd['comment']
        if not self.err:
            self.wpt.put()
            self.redirect('/myvessel')
        else:
            self.get(self.err, self.fd)

    def add_coords(self):
        pt = Point()
        try:
            pt.set_lat(self.fd['latdeg'], self.fd['latmin'])
        except InvalidPointError as point_err:
            self.err['lat'] = str(point_err)
        try:
            pt.set_lon(self.fd['londeg'], self.fd['lonmin'])
        except InvalidPointError as point_err:
            self.err['lon'] = str(point_err)
        self.wpt.position = ndb.GeoPt(pt.lat, pt.lon)


application = WSGIApplication([('/myvessel', MyVesselPage),
                               ('/vessel/key/(.+)', VesselPage),
                               ('/posreport/key/(.+)', WebPositionReport),
                               ])
