from __future__ import absolute_import, unicode_literals
import os

import django
from celery import Celery

# set the default Django settings module for the 'celery' program.
from project.settings import IS_DOCKER

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'project.settings')
django.setup()
from project import tghandler

if IS_DOCKER:
    REDIS_HOST = 'redis'
else:
    REDIS_HOST = '127.0.0.1'
app = Celery('project')
app.conf.broker_url = f'redis://{REDIS_HOST}:6379/0'
# Using a string here means the worker don't have to serialize
# the configuration object to child processes.
# - namespace='CELERY' means all celery-related configuration keys
#   should have a `CELERY_` prefix.
app.config_from_object('django.conf:settings', namespace='CELERY')

app.conf.beat_schedule = {
    # 'ping-every-60-seconds': {
    #     'task': 'project.tgbot.tasks.ping_all',
    #     'schedule': 60
    # },
}

# Load task modules from all registered Django app configs.
app.autodiscover_tasks()
