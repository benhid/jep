import os
import uuid
from urllib.error import URLError
from urllib.request import urlopen

from celery import states
from celery.signals import worker_ready, worker_shutdown, heartbeat_sent

from worker import celery_app

AGENT_UNIQUE_ID = str(uuid.uuid1())
EXECUTOR_PLATFORM_ID = os.getenv('EXECUTOR_PLATFORM_ID')
EXECUTOR_VERSION_ID = os.getenv('EXECUTOR_VERSION_ID')


@worker_ready.connect
@heartbeat_sent.connect
def register_agent(sender, **k):
    celery_app.signature(
        'join_group',
        kwargs={
            'tasks': [
                {'name': 'open_web', 'description': 'return web as string'},
            ],
            'agent_id': AGENT_UNIQUE_ID,
            'executor_platform_id': EXECUTOR_PLATFORM_ID,
            'executor_version_id': EXECUTOR_VERSION_ID
        },
        queue='events'
    ).delay(expires=1)

    return f'agent joined on queue {EXECUTOR_PLATFORM_ID}-{EXECUTOR_VERSION_ID}'


@worker_shutdown.connect
def unregister_agent(sender, **k):
    celery_app.signature(
        'disjoin_group',
        kwargs={'agent_id': AGENT_UNIQUE_ID},
        queue='events'
    ).delay()

    return f'agent disconnected from queue {EXECUTOR_PLATFORM_ID}-{EXECUTOR_VERSION_ID}'


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
