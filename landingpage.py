import webapp2

class LandingPage(webapp2.RequestHandler):

    def get(self):
        self.response.write('Hello sailing world!')


application = webapp2.WSGIApplication([
    ('/', LandingPage),
], debug=True)