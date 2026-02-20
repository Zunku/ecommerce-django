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

CELERY_BROKER_URL = 'redis://localhost:6379/1'

CACHES = {
    "default": {
        "BACKEND": "django_redis.cache.RedisCache",
        "LOCATION": "redis://localhost:6379/2",
        "TIMEOUT":10*60,
        "OPTIONS": {
            "CLIENT_CLASS": "django_redis.client.DefaultClient",
        }
    }
}

# Email backend configuration
EMAIL_HOST = 'localhost'
EMAIL_HOST_USER = ''
EMAIL_HOST_PASSWORD = ''
EMAIL_PORT = 2525
DEFAULT_FROM_EMAIL = 'form@zunkubuy.com'