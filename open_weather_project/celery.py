import os
from celery import Celery
from django.conf import settings

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'open_weather_project.settings')

app = Celery('open_weather_project')

# This reads the CELERY configurations from settings.py
app.config_from_object('django.conf:settings', namespace='CELERY')

# This will make sure the app always imports when
# Django starts so that the `shared_task` will use this app.
app.autodiscover_tasks(lambda: settings.INSTALLED_APPS)
