import logging
import os

from celery import Celery

# app logger
logger = logging.getLogger('je-platform-agent')

handler = logging.StreamHandler()
handler.setFormatter(logging.Formatter('%(asctime)s - %(message)s'))

logger.addHandler(handler)
logger.setLevel(logging.DEBUG)

info = logger.info
debug = logger.debug
warning = logger.warning

# celery
CELERY_BROKER_HOST = os.environ['CELERY_BROKER_HOST']
CELERY_BROKER_PORT = os.environ['CELERY_BROKER_PORT']
CELERY_BROKER_USERNAME = os.environ['CELERY_BROKER_USERNAME']
CELERY_BROKER_PASSWORD = os.environ['CELERY_BROKER_PASSWORD']

celery_app = Celery('je-platform',
                    broker=f'amqp://{CELERY_BROKER_USERNAME}:{CELERY_BROKER_PASSWORD}@{CELERY_BROKER_HOST}:{CELERY_BROKER_PORT}//',
                    backend='amqp')
