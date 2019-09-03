import logging
import os

from celery import Celery

# app logger
logger = logging.getLogger('je-platform-server')

handler = logging.StreamHandler()
handler.setFormatter(logging.Formatter('%(asctime)s - %(message)s'))

logger.addHandler(handler)
logger.setLevel(logging.DEBUG)

info = logger.info
debug = logger.debug
warning = logger.warning

# server env variables
API_HOST = os.environ['API_HOST']
API_PORT = os.environ['API_PORT']

# mongo
DATABASE_HOST = os.environ['DATABASE_HOST']
DATABASE_PORT = os.environ['DATABASE_PORT']
DATABASE_USERNAME = os.environ['DATABASE_USERNAME']
DATABASE_PASSWORD = os.environ['DATABASE_PASSWORD']

# celery
CELERY_BROKER_HOST = os.environ['CELERY_BROKER_HOST']
CELERY_BROKER_PORT = os.environ['CELERY_BROKER_PORT']
CELERY_BROKER_USERNAME = os.environ['CELERY_BROKER_USERNAME']
CELERY_BROKER_PASSWORD = os.environ['CELERY_BROKER_PASSWORD']

celery_app = Celery('je-platform',
                    broker=f'amqp://{CELERY_BROKER_USERNAME}:{CELERY_BROKER_PASSWORD}@{CELERY_BROKER_HOST}:{CELERY_BROKER_PORT}//',
                    backend='amqp')
