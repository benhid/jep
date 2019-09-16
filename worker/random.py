import os
import random
import time

from celery.signals import worker_ready

from worker import celery_app


@worker_ready.connect
def register_agent(sender, **k):
    executor_platform_id = os.getenv('EXECUTOR_PLATFORM_ID')
    executor_version_id = os.getenv('EXECUTOR_VERSION_ID')

    celery_app.signature(
        'join_group',
        kwargs={'executor_platform_id': executor_platform_id, 'executor_version_id': executor_version_id},
        queue='events'
    ).delay()

    return f'agent joined on queue {executor_platform_id}-{executor_version_id}'


@celery_app.task(name='random', track_started=True, default_retry_delay=2, max_retries=3, acks_late=True, bind=True)
def random_generator(self, data):
    time.sleep(random.randint(5, 15))
    result = [random.randint(0, 10) for _ in range(100)]

    def on_failure(self, *args, **kwargs):
        pass

    return ' '.join(map(str, result))
