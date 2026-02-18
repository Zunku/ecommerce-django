import os
from .common import *

DEBUG = False

SECRET_KEY = os.environ['SECRET_KEY']

# Servers that can run this application, required if debug is turn off
ALLOWED_HOSTS = []