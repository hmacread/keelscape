#-*- coding: utf-8 -*-
# datamodel.py
# Created by Hugh Macready (hugh@macready.id.au)
# Data model to be used is NDB for Google App Engine
#
from google.appengine.api import users
from google.appengine.ext import ndb

from geocal.point import Point

class Owner(ndb.Model):

    """Represents an owner of a vessel."""

    id = ndb.StringProperty()
    email = ndb.StringProperty()
    nickname = ndb.StringProperty()

    @classmethod
    def exists(cls, user=None, email=None):
        u"""Test for existence of a user.

        :param email: use to check for vessels with that email address.
        :param user: user paramenter, if unspecified current user will be queried.
        :return: non-zero if the Owner exists.
        u"""
        if not user:
            user = users.get_current_user()
        return Owner.query(Owner.id == user.user_id()).count(limit=1)


    @classmethod
    def get_key(cls, user=None):
        u"""Return a key to an Owner object.

        :param user: Optional google user object, if not specified then current user is called.
        :return: ndb.Key for specified user, or current user if None.
        u"""
        if not user:
            user = users.get_current_user()
        return Owner.query(Owner.id == user.user_id()).get(keys_only=True)

    @classmethod
    def get(cls, user=None):
        return Owner.get_key(user).get()


def validate_callsign(property, value):

    value = value.strip()
    return value

class Vessel(ndb.Model):
    
    """Represents an secret-bay vessel"""

    name = ndb.StringProperty()
    email = ndb.StringProperty()
    home_port = ndb.StringProperty()
    flag = ndb.StringProperty()
    loa = ndb.FloatProperty() #in meters
    draft = ndb.FloatProperty() #in meters
    callsign = ndb.StringProperty(validator=validate_callsign)  #unique

    @classmethod
    def exists(cls, owner_key=None, email=None, callsign=None):
        if callsign:
            return Vessel.query(Vessel.callsign == callsign).count(limit=1)
        if email:
            return Vessel.query(Vessel.email == email).count(limit=1)
        if not owner_key:
            owner_key = Owner.get_key(users.get_current_user())
        return Vessel.query(ancestor=owner_key).count(limit=1)

    @classmethod
    def get_key(cls, owner_key=None):
        if not owner_key:
            owner_key = Owner.get_key(users.get_current_user())
        return Vessel.query(ancestor=owner_key).get(keys_only=True)

    @classmethod
    def get(cls, owner_key=None):
        return Vessel.get_key(owner_key).get()


class Waypoint(ndb.Model):

    """NDB datastore class for base class waypoint."""

    position = ndb.GeoPtProperty(required=True)
    comment = ndb.TextProperty()
    report_date = ndb.DateTimeProperty() 
    received_date = ndb.DateTimeProperty(required=True,auto_now_add=True)
    updated_date = ndb.DateTimeProperty(auto_now=True)
    course = ndb.StringProperty()
    speed = ndb.FloatProperty()
    depth = ndb.FloatProperty()

    @property
    def human_readable_lat(self):
        return Point.human_readable_lat(self.position.lat)

    @property
    def human_readable_lon(self):
        return Point.human_readable_lon(self.position.lon)

    def delete(self):
        self.key.delete()

class Weather(ndb.Model):
    
    """ NDB datastore object capturing the weather observation. 
    
    All measurements are in SI units, period in whole seconds, directions in 
    true degrees, speed in kts.
    """
    
    waypoint = ndb.KeyProperty(kind='Waypoint')
    wind_speed = ndb.FloatProperty()
    wind_direction = ndb.StringProperty()
    wind_waves_height = ndb.FloatProperty()
    wind_waves_period = ndb.IntegerProperty()
    primary_swell_height = ndb.FloatProperty()
    primary_swell_direction = ndb.StringProperty()
    primary_swell_period = ndb.IntegerProperty()
    barometric_pressure = ndb.FloatProperty()
    barometric_pressure_3hr_trend = ndb.FloatProperty()
    cloud_cover_percent = ndb.FloatProperty()
    visibility = ndb.FloatProperty()
    air_temperature = ndb.FloatProperty()
    sea_temperature = ndb.FloatProperty()

COUNTRIES = [
        u"Afghanistan",
        u"Åland Islands",
        u"Albania",
        u"Algeria",
        u"American Samoa",
        u"Andorra",
        u"Angola",
        u"Anguilla",
        u"Antarctica",
        u"Antigua and Barbuda",
        u"Argentina",
        u"Armenia",
        u"Aruba",
        u"Australia",
        u"Austria",
        u"Azerbaijan",
        u"Bahamas",
        u"Bahrain",
        u"Bangladesh",
        u"Barbados",
        u"Belarus",
        u"Belgium",
        u"Belize",
        u"Benin",
        u"Bermuda",
        u"Bhutan",
        u"Bolivia",
        u"Bosnia and Herzegovina",
        u"Botswana",
        u"Bouvet Island",
        u"Brazil",
        u"British Indian Ocean Territory",
        u"Brunei Darussalam",
        u"Bulgaria",
        u"Burkina Faso",
        u"Burundi",
        u"Cambodia",
        u"Cameroon",
        u"Canada",
        u"Cape Verde",
        u"Cayman Islands",
        u"Central African Republic",
        u"Chad",
        u"Chile",
        u"China",
        u"Christmas Island",
        u"Cocos (Keeling) Islands",
        u"Colombia",
        u"Comoros",
        u"Congo",
        u"Congo, The Democratic Republic of The",
        u"Cook Islands",
        u"Costa Rica",
        u"Cote D'ivoire",
        u"Croatia",
        u"Cuba",
        u"Cyprus",
        u"Czech Republic",
        u"Denmark",
        u"Djibouti",
        u"Dominica",
        u"Dominican Republic",
        u"Ecuador",
        u"Egypt",
        u"El Salvador",
        u"Equatorial Guinea",
        u"Eritrea",
        u"Estonia",
        u"Ethiopia",
        u"Falkland Islands (Malvinas)",
        u"Faroe Islands",
        u"Fiji",
        u"Finland",
        u"France",
        u"French Guiana",
        u"French Polynesia",
        u"French Southern Territories",
        u"Gabon",
        u"Gambia",
        u"Georgia",
        u"Germany",
        u"Ghana",
        u"Gibraltar",
        u"Greece",
        u"Greenland",
        u"Grenada",
        u"Guadeloupe",
        u"Guam",
        u"Guatemala",
        u"Guernsey",
        u"Guinea",
        u"Guinea-bissau",
        u"Guyana",
        u"Haiti",
        u"Heard Island and Mcdonald Islands",
        u"Holy See (Vatican City State)",
        u"Honduras",
        u"Hong Kong",
        u"Hungary",
        u"Iceland",
        u"India",
        u"Indonesia",
        u"Iran, Islamic Republic of",
        u"Iraq",
        u"Ireland",
        u"Isle of Man",
        u"Israel",
        u"Italy",
        u"Jamaica",
        u"Japan",
        u"Jersey",
        u"Jordan",
        u"Kazakhstan",
        u"Kenya",
        u"Kiribati",
        u"Korea, Democratic People's Republic of",
        u"Korea, Republic of",
        u"Kuwait",
        u"Kyrgyzstan",
        u"Lao People's Democratic Republic",
        u"Latvia",
        u"Lebanon",
        u"Lesotho",
        u"Liberia",
        u"Libyan Arab Jamahiriya",
        u"Liechtenstein",
        u"Lithuania",
        u"Luxembourg",
        u"Macao",
        u"Macedonia, The Former Yugoslav Republic of",
        u"Madagascar",
        u"Malawi",
        u"Malaysia",
        u"Maldives",
        u"Mali",
        u"Malta",
        u"Marshall Islands",
        u"Martinique",
        u"Mauritania",
        u"Mauritius",
        u"Mayotte",
        u"Mexico",
        u"Micronesia, Federated States of",
        u"Moldova, Republic of",
        u"Monaco",
        u"Mongolia",
        u"Montenegro",
        u"Montserrat",
        u"Morocco",
        u"Mozambique",
        u"Myanmar",
        u"Namibia",
        u"Nauru",
        u"Nepal",
        u"Netherlands",
        u"Netherlands Antilles",
        u"New Caledonia",
        u"New Zealand",
        u"Nicaragua",
        u"Niger",
        u"Nigeria",
        u"Niue",
        u"Norfolk Island",
        u"Northern Mariana Islands",
        u"Norway",
        u"Oman",
        u"Pakistan",
        u"Palau",
        u"Palestinian Territory, Occupied",
        u"Panama",
        u"Papua New Guinea",
        u"Paraguay",
        u"Peru",
        u"Philippines",
        u"Pitcairn",
        u"Poland",
        u"Portugal",
        u"Puerto Rico",
        u"Qatar",
        u"Reunion",
        u"Romania",
        u"Russian Federation",
        u"Rwanda",
        u"Saint Helena",
        u"Saint Kitts and Nevis",
        u"Saint Lucia",
        u"Saint Pierre and Miquelon",
        u"Saint Vincent and The Grenadines",
        u"Samoa",
        u"San Marino",
        u"Sao Tome and Principe",
        u"Saudi Arabia",
        u"Senegal",
        u"Serbia",
        u"Seychelles",
        u"Sierra Leone",
        u"Singapore",
        u"Slovakia",
        u"Slovenia",
        u"Solomon Islands",
        u"Somalia",
        u"South Africa",
        u"South Georgia and The South Sandwich Islands",
        u"Spain",
        u"Sri Lanka",
        u"Sudan",
        u"Suriname",
        u"Svalbard and Jan Mayen",
        u"Swaziland",
        u"Sweden",
        u"Switzerland",
        u"Syrian Arab Republic",
        u"Taiwan, Province of China",
        u"Tajikistan",
        u"Tanzania, United Republic of",
        u"Thailand",
        u"Timor-leste",
        u"Togo",
        u"Tokelau",
        u"Tonga",
        u"Trinidad and Tobago",
        u"Tunisia",
        u"Turkey",
        u"Turkmenistan",
        u"Turks and Caicos Islands",
        u"Tuvalu",
        u"Uganda",
        u"Ukraine",
        u"United Arab Emirates",
        u"United Kingdom",
        u"United States",
        u"United States Minor Outlying Islands",
        u"Uruguay",
        u"Uzbekistan",
        u"Vanuatu",
        u"Venezuela",
        u"Viet Nam",
        u"Virgin Islands, British",
        u"Virgin Islands, U.S.",
        u"Wallis and Futuna",
        u"Western Sahara",
        u"Yemen",
        u"Zambia",
        u"Zimbabwe",
]