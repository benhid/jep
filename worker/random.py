import os
import random
import time
import uuid

from celery.signals import worker_ready, worker_shutdown

from worker import celery_app

AGENT_UNIQUE_ID = uuid.uuid1()
EXECUTOR_PLATFORM_ID = os.getenv('EXECUTOR_PLATFORM_ID')
EXECUTOR_VERSION_ID = os.getenv('EXECUTOR_VERSION_ID')


@worker_ready.connect
def register_agent(sender, **k):
    celery_app.signature(
        'join_group',
        kwargs={
            'tasks': [
                {'name': 'random', 'description': 'return list of random numbers as string (comma-separated)'},
            ],
            'agent_id': AGENT_UNIQUE_ID,
            'executor_platform_id': EXECUTOR_PLATFORM_ID,
            'executor_version_id': EXECUTOR_VERSION_ID
        },
        queue='events'
    ).delay()

    return f'agent joined on queue {EXECUTOR_PLATFORM_ID}-{EXECUTOR_VERSION_ID}'


@worker_shutdown.connect
def unregister_agent(sender, **k):
    celery_app.signature(
        'disjoin_group',
        kwargs={'agent_id': AGENT_UNIQUE_ID},
        queue='events'
    ).delay()

    return f'agent disconnected from queue {EXECUTOR_PLATFORM_ID}-{EXECUTOR_VERSION_ID}'


@celery_app.task(name='random', track_started=True, default_retry_delay=2, max_retries=3, acks_late=True, bind=True)
def random_generator(self, data):
    time.sleep(random.randint(5, 15))
    result = [random.randint(0, 10) for _ in range(100)]

    def on_failure(self, *args, **kwargs):
        pass

    return ' '.join(map(str, result))
