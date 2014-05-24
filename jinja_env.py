__author__ = 'hmacread'

import os
from jinja2 import Environment, FileSystemLoader

#Jinja Environment instanciation to be used.
JINJA_ENV = Environment(
    loader=FileSystemLoader(os.path.dirname(__file__) + '/templates'),
    extensions=['jinja2.ext.autoescape'],
    autoescape=True
)