# Keelscape

http://www.keelscape.com

A web application designed to facilitate sharing of waypoints, tracks, route maps within the world cruising community and their freinds and family.

## Developer Setup

In order to run the project locallyi: 

1. Follow the instructions to install the Google App Engine SDK for Python for your environment here:
	_https://developers.google.com/appengine/downloads_
2. Generaate your own Google Maps Embedded API key by following the instructinos here:
	_https://developers.google.com/maps/documentation/embed/guide#api_key_
3. Edit configdata.py and change GMAPS_EMBED_API_KEY to be your newly created key.

4. Run `python dev_appserver.py --host 127.0.0.1`
