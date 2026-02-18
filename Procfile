# Command executed each release
release: python manage.py migrate

# Web process to start application
web: gunicorn storefront.wsgi

# Worker of Celery
worker: celery -A storefront worker