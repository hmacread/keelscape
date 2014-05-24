__author__ = 'hmacread'

from webapp2 import WSGIApplication, RequestHandler

from datamodel import *
from jinja_env import JINJA_ENV

class VesselPage(RequestHandler):

    NUM_WAYPOINTS = 5
    GMAPS_EMBED_API_KEY = "AIzaSyBMhILdBdcbYKlKzYg3WeiMfO_Y0tFd-XM"

    def get_template_params(self, vessel_key):
        vessel = vessel_key.get()
        wpt_qry = Waypoint.query(ancestor=vessel.key).order(-Waypoint.report_date)
        if wpt_qry.count(limit=1):
            map_url = ("https://www.google.com/maps/embed/v1/place" +
                       "?key=" + self.GMAPS_EMBED_API_KEY +
                       "&q=" + str(wpt_qry.get().position) +
                       "&zoom=5" +
                       "&maptype=satellite"
                       )
        else:
            map_url = ("https://www.google.com/maps/embed/v1/view" +
                       "?key=" + self.GMAPS_EMBED_API_KEY +
                       "&center=0,%200" +
                       "&zoom=1" +
                       "&maptype=satellite"
                       )

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
        #call super class
        params = VesselPage.get_template_params(self, vessel_key)
        #add myvessel specific data
        params.update({'user': users.get_current_user(),
                       'pulic_link': '/vessel/key/' + vessel_key.urlsafe(),
                       'submit_wpt_url': '/posreport/key/' + vessel_key.urlsafe(),
                       'logouturl': users.create_logout_url('/'),
                       })
        return params

    #Authentication enforced by app.yaml
    def get(self):
        vessel_key = Vessel.get_key()
        if not Vessel.exists():
            #owner got here without creating a vessel somehow
            self.redirect('/newvessel')
        template = JINJA_ENV.get_template('myvessel.html')
        self.response.write(template.render(self.get_template_params(vessel_key)))

application = WSGIApplication([('/myvessel', MyVesselPage),
                               ('/vessel/key/(.+)', VesselPage),
                               ])