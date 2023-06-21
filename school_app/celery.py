from celery import Celery
import os


os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'school_app.settings')
app = Celery('school_app')

app.config_from_object('django.conf:settings', namespace='CELERY')

app.autodiscover_tasks()
