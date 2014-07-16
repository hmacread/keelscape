from google.appengine.ext import ndb
from webapp2 import RequestHandler, WSGIApplication
from datamodel import Owner
from geocal.point import Point
from mapping import GoogleMapWpt
from jinja_env import JINJA_ENV
from vessel import WebPositionReport

__author__ = 'hmacread'

class WptDeleteRequest(RequestHandler):

    def get(self, wpt_key_str):
        wpt_key = ndb.Key(urlsafe=wpt_key_str)
        this_owner = Owner.get_key()
        #assumes that wpts are only children of vessels that are in turn children of owners
        wpt_owner = wpt_key.parent().parent()

        if this_owner == wpt_owner:
            wpt_key.delete()
            url = '/myvessel'
            if self.request.get('cursor'):
                  url += '?cursor=' + self.request.get('cursor')
            self.redirect(url)
        else:
            self.response.out.http_status_message(403)

class Waypoint(RequestHandler):

    def add_params(self):
        pass

    def get(self, wpt_key_str):
        params = {}
        wpt_key = ndb.Key(urlsafe=wpt_key_str)
        wpt = wpt_key.get()
        params['wpt'] = wpt
        params['map'] = GoogleMapWpt(wpt)
        params['vessel'] = wpt.key.parent().get()
        template = JINJA_ENV.get_template(self.template_name())
        self.response.write(template.render(params))

    def template_name(self):
        return 'waypoint.html'

class EditWpt(Waypoint, WebPositionReport):

    def template_name(self):
        return 'waypoint_edit.html'

    def post(self, wpt_key_str):

        self.wpt = ndb.Key(urlsafe=wpt_key_str).get()
        self.add_all()
        if not self.err:
            self.wpt.put()
            self.redirect('/waypoint/' + wpt_key_str)
        else:
            self.get(wpt_key_str, self.err, self.request.POST)

    def get(self, wpt_key_str, form_errs=None, form_content=None):
        wpt_key = ndb.Key(urlsafe=wpt_key_str)
        wpt = wpt_key.get()
        print form_errs
        #Gather database material
        pt = Point(wpt.position.lat, wpt.position.lon)
        params = {
            'dirlat' : pt.dirlat,
            'dirlon' : pt.dirlon,
            'latdeg' : pt.latdeg,
            'latmin' : pt.latmin,
            'londeg' : pt.londeg,
            'lonmin' : pt.lonmin,
            'report_date' : wpt.report_date.strftime('%Y-%m-%d %H:%M')
        }

        if wpt.depth:
            params['depth'] = wpt.depth
        if wpt.speed:
            params['speed'] = wpt.speed
        if wpt.course:
            params['course'] = wpt.course

        #overwrite with previous update attempt if present
        if form_content:
            params.update(form_content)

        #pass a dict of errors to the template
        if form_errs:
            params['errors'] = form_errs

        params['wpt'] = wpt
        params['map'] = GoogleMapWpt(wpt)
        params['vessel'] = wpt.key.parent().get()
        template = JINJA_ENV.get_template(self.template_name())
        self.response.write(template.render(params))



application = WSGIApplication([
    ('/waypoint/delete/(.+)', WptDeleteRequest),
    ('/waypoint/edit/(.+)', EditWpt),
    ('/waypoint/(.+)', Waypoint),
    ])