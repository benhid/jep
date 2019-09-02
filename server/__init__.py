import logging
import os

from celery import Celery

# app logger
logger = logging.getLogger('je-platform-server')

handler = logging.StreamHandler()
handler.setFormatter(logging.Formatter('%(asctime)s - %(name)s - %(message)s'))

logger.addHandler(handler)
logger.setLevel(logging.DEBUG)

info = logger.info
debug = logger.debug
warning = logger.warning

# server env variables
API_HOST = os.getenv('API_HOST', '192.168.48.222')
API_PORT = os.getenv('API_PORT', 6565)

# celery
RABBIT_HOST = os.getenv('RABBIT_HOST', '127.0.0.1')
RABBIT_PORT = os.getenv('RABBIT_PORT', 5672)
RABBIT_USERNAME = os.getenv('RABBIT_USERNAME', 'rabbit')
RABBIT_PASSWORD = os.getenv('RABBIT_PASSWORD', 'rabbit')

celery_app = Celery('je-platform',
                    broker=f'amqp://{RABBIT_USERNAME}:{RABBIT_PASSWORD}@{RABBIT_HOST}:{RABBIT_PORT}//',
                    backend='amqp')
