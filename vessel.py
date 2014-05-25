__author__ = 'hmacread'

from webapp2 import WSGIApplication, RequestHandler

from datamodel import *
from jinja_env import JINJA_ENV

import secretdata

class VesselPage(RequestHandler):

    NUM_WAYPOINTS = 5

    def map_url(self, q=None, zoom=1, maptype="satellite"):

        url = "https://www.google.com/maps/embed/v1/"
        if q:
            return (url + "place" +
                    "?key=" + secretdata.GMAPS_EMBED_API_KEY +
                    "&q=" + q +
                    "&zoom=" + str(zoom) +
                    "&maptype=" + maptype
                    )
        else:
            return (url + "view" +
                    "?key=" + secretdata.GMAPS_EMBED_API_KEY +
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
                       'pulic_link': '/vessel/key/' + vessel_key.urlsafe(),
                       'submit_wpt_url': '/posreport/key/' + vessel_key.urlsafe(),
                       'logouturl': users.create_logout_url('/'),
                       })
        return params

    #Authentication enforced by app.yaml
    def get(self):
        if not Vessel.exists():
            #owner got here without creating a vessel somehow
            self.redirect('/newvessel')
        else:
            vessel_key = Vessel.get_key()
            template = JINJA_ENV.get_template('myvessel.html')
            self.response.write(template.render(self.get_template_params(vessel_key)))

application = WSGIApplication([('/myvessel', MyVesselPage),
                               ('/vessel/key/(.+)', VesselPage),
                               ])