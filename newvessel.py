__author__ = 'hmacread'

from webapp2 import WSGIApplication, RequestHandler
from jinja_env import JINJA_ENV
from datamodel import *

class NewVesselPage(RequestHandler):

    def get(self):

        user = users.get_current_user()
        vessel = get_vessel(user)
        template = JINJA_ENV.get_template('newvessel.html')
        self.response.write(template.render(
            vessel=vessel,
            user=user,
            logouturl=users.create_logout_url('/'),
            errormsg='',
        ))

    def put_values(self, vessel):

        data = self.request.POST

        #check name and email exist
        if not data['name']:
            raise NewVesselError('Please enter an vessel name.')
        self.vessel.name = data['name']
        if not data['email']:
            raise NewVesselError('Please enter an email address.')

        #check uniqueness of email or callsign
        if Vessel.query(Vessel.callsign == data['email']).count():
            raise NewVesselError('Sorry ' + data['email'] + ' is already in use.')
        if data['callsign'] and Vessel.query(Vessel.callsign == data['callsign']).count():
            raise NewVesselError('The callsign ' + data['callsign'] + ' is already in use.')

        #TODO finish new vessel code
        self.vessel.put()
        logging.info('got here')

    def post(self):

        user = users.get_current_user()
        self.vessel = Vessel(parent=Owner.get_key())
        try:
            self.put_values(self.vessel)
            self.redirect('/myvessel')
        except NewVesselError as error:
            template = template = JINJA_ENV.get_template('newvessel.html')
            self.response.write(template.render(
                vessel=self.vessel,
                user=user,
                logouturl=users.create_logout_url('/'),
                errormsg=str(error)
                ))

application = WSGIApplication([('/newvessel', NewVesselPage)])