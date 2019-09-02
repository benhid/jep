import os
import subprocess

from celery.signals import worker_ready

from agent import info, celery_app


@worker_ready.connect
def register_agent(sender, **k):
    executor_platform_id = os.getenv('EXECUTOR_PLATFORM_ID')
    executor_version_id = os.getenv('EXECUTOR_VERSION_ID')

    print(f'agent joined on queue {executor_platform_id}-{executor_version_id}')


@celery_app.task(name='run_local_script', default_retry_delay=2, max_retries=3, acks_late=True, bind=True)
def process_script(self, msg):
    try:
        pcs = execute(f'python -c "{msg}"')
        result = pcs.stdout
    except Exception:
        raise

    def on_failure(self, *args, **kwargs):
        pass

    return result.splitlines()


@celery_app.task(name='run_local_file', default_retry_delay=2, max_retries=3, acks_late=True, bind=True)
def process_file(self, msg):
    try:
        pcs = execute(f'python "{msg}"')
        result = pcs.stdout
    except Exception:
        raise

    def on_failure(self, *args, **kwargs):
        pass

    return result.splitlines()


def execute(command: str):
    # we are making some assumptions here (such as the input script is SAFE to run)
    pcs = subprocess.run(command,
                         universal_newlines=True,
                         shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)

    info(f'task returned {pcs.returncode}')
    info(f'output stdout {pcs.stdout}')
    info(f'output stderr {pcs.stderr}')

    if pcs.stderr:
        raise Exception(pcs.stderr)

    return pcs
