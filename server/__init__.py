import logging
import os

from celery import Celery

# app logger
logger = logging.getLogger('JEplatform[server]')

handler = logging.StreamHandler()
handler.setFormatter(logging.Formatter('JEplatform [server] %(asctime)s - %(message)s'))

logger.addHandler(handler)
logger.setLevel(logging.DEBUG)

info = logger.info
debug = logger.debug
warning = logger.warning

# server env variables
API_HOST = os.environ['API_HOST']
API_PORT = os.environ['API_PORT']
API_KEY = os.environ['API_KEY']

# mongo
API_DB_HOST = os.environ['API_DB_HOST']
API_DB_PORT = os.environ['API_DB_PORT']
API_DB_USERNAME = os.environ['API_DB_USERNAME']
API_DB_PASSWORD = os.environ['API_DB_PASSWORD']

# celery
CELERY_BROKER_HOST = os.environ['CELERY_BROKER_HOST']
CELERY_BROKER_PORT = os.environ['CELERY_BROKER_PORT']
CELERY_BROKER_USERNAME = os.environ['CELERY_BROKER_USERNAME']
CELERY_BROKER_PASSWORD = os.environ['CELERY_BROKER_PASSWORD']

CELERY_DB_HOST = os.environ['CELERY_DB_HOST']
CELERY_DB_PORT = os.environ['CELERY_DB_PORT']
CELERY_DB_USERNAME = os.environ['CELERY_DB_USERNAME']
CELERY_DB_PASSWORD = os.environ['CELERY_DB_PASSWORD']

celery_app = Celery('JEplatform',
                    broker=f'amqp://{CELERY_BROKER_USERNAME}:{CELERY_BROKER_PASSWORD}@{CELERY_BROKER_HOST}:{CELERY_BROKER_PORT}//',
                    backend=f'redis://{CELERY_DB_HOST}:{CELERY_DB_PORT}/0')
