import os
import subprocess
import uuid

from celery import states
from celery.signals import worker_ready, worker_shutdown

from worker import info, celery_app

AGENT_UNIQUE_ID = uuid.uuid1()
EXECUTOR_PLATFORM_ID = os.getenv('EXECUTOR_PLATFORM_ID')
EXECUTOR_VERSION_ID = os.getenv('EXECUTOR_VERSION_ID')


@worker_ready.connect
def register_agent(sender, **k):
    celery_app.signature(
        'join_group',
        kwargs={
            'tasks': [
                {'name': 'run_script_py', 'description': 'execute python script from command line'},
                {'name': 'run_local_file_py', 'description': 'execute python script from local dir'}
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


@celery_app.task(name='run_script_py', track_started=True, default_retry_delay=2, max_retries=3, acks_late=True,
                 bind=True)
def process_script(self, data):
    try:
        pcs = execute(f'python -c "{data}"')
        result = pcs.stdout
    except Exception:
        self.update_state(state=states.FAILURE, meta={'exception': f'python -c "{data}"', 'script': data})
        raise

    def on_failure(self, *args, **kwargs):
        pass

    return result.splitlines()


@celery_app.task(name='run_local_file_py', track_started=True, default_retry_delay=2, max_retries=3, acks_late=True,
                 bind=True)
def process_file(self, data):
    try:
        pcs = execute(f'python "{data}"')
        result = pcs.stdout
    except Exception:
        self.update_state(state=states.FAILURE, meta={'exception': f'python "{data}"', 'filename': data})
        raise

    def on_failure(self, *args, **kwargs):
        pass

    return result.splitlines()


def execute(command: str):
    # we are making some assumptions here (such as the input script is SAFE to run)
    pcs = subprocess.run(command,
                         universal_newlines=True,
                         shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)

    info(f'job returned {pcs.returncode}')
    info(f'output stdout {pcs.stdout}')
    info(f'output stderr {pcs.stderr}')

    if pcs.stderr:
        raise Exception(pcs.stderr)

    return pcs
