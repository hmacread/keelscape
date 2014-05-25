# emailhandler.py
# Created by Hugh Macready (hugh@macready.id.au)
# Inbound email position report handler script

import logging
import webapp2
import positionreport
import datamodel

from google.appengine.ext.webapp.mail_handlers import InboundMailHandler

class PositionReportMailHandler(InboundMailHandler):
    
    def receive(self, message):
    
        logging.info("Received a message from: " + message.sender)
        plaintext_bodies = message.bodies('text/plain')
        body_count = 0
        for content_type, body in plaintext_bodies:        
            body_count += 1
            #return an iterator to an upper case only enumeration of email lines    
            body_iterator = enumerate(body.decode().splitlines())
            report = positionreport.PositionReport(body_iterator)
            report.put_contents()
              
        if not body_count > 0:
            raise PositionReportError(0,"<No plain text body found in message>")
        
#webapp2 attribute 
application = webapp2.WSGIApplication([PositionReportMailHandler.mapping()])