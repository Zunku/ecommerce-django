import os
from celery import Celery

# Creating an env variable
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'storefront.settings')

# Instancing celery
celery = Celery('storefront')

# Loading settings object from django, all our configurations will start with CELLERY
celery.config_from_object('django.conf:settings', namespace='CELERY')

# Load tasks from all tasks.py modules in our project
celery.autodiscover_tasks()

# You have to import this module from __init__