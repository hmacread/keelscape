""" Copyright 2018 Hugh Macready

Licensed under the Apache License, Version 2.0 (the "License");
you may not use this file except in compliance with the License.
You may obtain a copy of the License at

    http://www.apache.org/licenses/LICENSE-2.0

Unless required by applicable law or agreed to in writing, software
distributed under the License is distributed on an "AS IS" BASIS,
WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
See the License for the specific language governing permissions and
limitations under the License.
"""

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