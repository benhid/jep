import os
import subprocess

from celery import states
from celery.signals import worker_ready

from worker import info, celery_app


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


@celery_app.task(name='run_script_py', track_started=True, default_retry_delay=2, max_retries=3, acks_late=True, bind=True)
def process_script(self, data):
    try:
        pcs = execute(f'python -c "{data}"')
        result = pcs.stdout
    except Exception:
        self.update_state(state=states.FAILURE, meta={'Exception': f'python -c "{data}"'})
        raise

    def on_failure(self, *args, **kwargs):
        pass

    return result.splitlines()


@celery_app.task(name='run_local_file_py', track_started=True, default_retry_delay=2, max_retries=3, acks_late=True, bind=True)
def process_file(self, data):
    try:
        pcs = execute(f'python "{data}"')
        result = pcs.stdout
    except Exception:
        self.update_state(state=states.FAILURE, meta={'Exception': f'python "{data}"'})
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
