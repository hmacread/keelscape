# emailhandler.py
# Created by Hugh Macready (hugh@macready.id.au)
# Inbound email position report handler script

import logging
import webapp2
import positionreport

from google.appengine.ext.webapp.mail_handlers import InboundMailHandler

class PositionReportMailHandler(InboundMailHandler):
    
    def receive(self, message):
        plaintext_bodies = message.bodies('text/plain')
        body_count = 0
        for content_type, body in plaintext_bodies:        
            body_count += 1
            # TODO split out all forwarded emails surrounded by ------ dividers Airmail style here
            #return an iterator to an upper case only enumeration of email lines
            body_iterator = enumerate(body.decode().splitlines())
            report = positionreport.PositionReport(body_iterator)
            report.put_contents()

        logging.info("Processed a message from: " + message.sender + " with " + str(body_count) + " body(ies).")
        if not body_count > 0:
            raise positionreport.PositionReportError(0, "<No plain text body found in message>")
        
#webapp2 attribute 
application = webapp2.WSGIApplication([PositionReportMailHandler.mapping()], debug=True)