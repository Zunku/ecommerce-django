from .common import *

DEBUG = True

SECRET_KEY = 'django-insecure-#vg1_^tg)p8)45nbv=du0*ekvj*qblff0+l25cir+31wqp&w&9'

MIDDLEWARE += ['silk.middleware.SilkyMiddleware']

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql_psycopg2',
        'NAME': 'storefront',
        'USER': 'postgres',
        'PASSWORD': 'PuzzlePost',
        'HOST': 'localhost',
        'PORT': '5432'
    }
}