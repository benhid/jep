import os
from urllib.error import URLError
from urllib.request import urlopen

from celery import states
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


@celery_app.task(name='open_web', track_started=True, default_retry_delay=2, max_retries=3, acks_late=True, bind=True)
def process_script(self, data):
    try:
        web = urlopen(data)
        result = web.read()
    except ValueError:
        self.update_state(state=states.FAILURE, meta={'exception': 'URL not well formatted', 'url': data})
        raise
    except URLError:
        self.update_state(state=states.FAILURE, meta={'exception': 'URL do not seem to be alive', 'url': data})
        raise

    def on_failure(self, *args, **kwargs):
        pass

    return str(result)
