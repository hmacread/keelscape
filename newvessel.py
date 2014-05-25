import logging
import string
import re
from webapp2 import WSGIApplication, RequestHandler
from jinja_env import JINJA_ENV
from google.appengine.api.datastore_errors import BadValueError
from datamodel import *

__author__ = 'hmacread'

# noinspection PyMissingConstructor
class AlreadyExistsError(Exception):
    pass

class NewVesselPage(RequestHandler):
    def __init__(self, request, response):
        RequestHandler.initialize(self, request, response)
        self.fd = self.request.POST
        self.vessel = Vessel(parent=Owner.get_key())
        self.valid = True

    def get(self, extra_params=None):
        template = JINJA_ENV.get_template('newvessel.html')
        params = {'user': users.get_current_user(),
                  'logouturl': users.create_logout_url('/'),
                  'email': users.get_current_user().email()
                  }
        if extra_params:
            params.update(extra_params)
        self.response.write(template.render(params))

    def add_name(self):
        """Adds mandatory valid name."""
        try:
            for word in self.fd['name'].split():
                assert word.isalnum()
            self.vessel.name = self.fd['name'].strip()
            assert 0 < len(self.vessel.name) <= 100
        except(ValueError, TypeError, BadValueError, AssertionError):
            self.fd.update({'name_err': "Please enter your vessel name (up 100 letter, numbers or spaces)."})
            self.valid = False

    def add_email(self):
        """Adds mandatory valid email."""
        try:
            try:
                assert re.match("[^@]+@[^@]+\.[^@]+", self.fd['email'])
                self.vessel.email = self.fd['email']
                if Vessel.exists(email=str(self.fd['email'])):
                    raise AlreadyExistsError()

            except(ValueError, TypeError, BadValueError, AssertionError):
                self.fd.update({'email_err': "Please enter a valid email address for this vessel that we can contact."})
                self.valid = False
        except AlreadyExistsError:
            self.fd.update({'email_err': "This email address already exists in the database."})
            self.valid = False

    def add_home_port(self):
        if self.fd['home_port']:
            try:
                self.vessel.home_port = string.capwords(self.fd['home_port'])
                assert 0 < len(self.vessel.home_port) <= 100
            except(ValueError, TypeError, BadValueError, AssertionError):
                self.fd.update({'home_port_err': "Your home port can be up to 100 letters."})
                self.valid = False

    def add_flag(self):
        if self.fd['flag']:
            try:
                self.vessel.flag = string.capwords(self.fd['flag'])
                assert 0 < len(self.vessel.flag) <= 100
            except(ValueError, TypeError, BadValueError, AssertionError):
                self.fd.update({'flag_err': "Your flag (home country) can be up to 100 letters."})
                self.valid = False

    def add_draft(self):
        """Checks for the optional parameter draft and adds to vessel."""
        if self.fd['draft']:
            try:
                self.vessel.draft = float(self.fd['draft'].strip())
                assert 0 <= self.vessel.draft <= 30
            except(ValueError, TypeError, BadValueError, AssertionError):
                self.fd.update({'draft_err': "You may enter a draft between 0.0 and 30.0 meters."})
                self.valid = False

    def add_loa(self):
        if self.fd['loa']:
            try:
                self.vessel.loa = float(self.fd['loa'])
                assert 0 <= self.vessel.loa <= 600
            except(ValueError, TypeError, BadValueError, AssertionError):
                self.fd.update({'loa_err': "You may enter a vessel length between 0.0 and 600.0 meters."})
                self.valid = False

    def add_callsign(self):
        """Adds optional valid callsign."""
        if self.fd['callsign']:
            try:
                try:
                    self.vessel.callsign = str(self.fd['callsign']).strip().upper()
                    assert self.vessel.callsign.isalnum()
                    if Vessel.exists(callsign=str(self.fd['callsign'])):
                        raise AlreadyExistsError()
                except(ValueError, TypeError, BadValueError, AssertionError):
                    self.fd.update({'callsign_err': "Please enter a valid HF callsign."})
                    self.valid = False
            except AlreadyExistsError:
                self.fd.update({'callsign_err': "Callsign %s already exists in the database." % self.vessel.callsign})
                self.valid = False

    def post(self):

        self.add_name()
        self.add_email()
        self.add_flag()
        self.add_home_port()
        self.add_draft()
        self.add_loa()
        self.add_callsign()

        if self.valid and self.vessel.put():
            logging.info("New vessel added: " + self.vessel.name)
            self.redirect('/myvessel')
        else:
            self.fd.update({'error_msg': "There was one or more problems with your vessel information.  See above."})
            self.get(self.fd)


application = WSGIApplication([('/newvessel', NewVesselPage)])