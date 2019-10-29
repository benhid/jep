import requests

from server import *


@celery_app.task(name='join_group', track_started=True, default_retry_delay=2, max_retries=3, acks_late=True, bind=True)
def process_script(self, tasks: dict, agent_id: str, **kwargs):
    executor_version_id = kwargs.get('executor_version_id')
    executor_platform_id = kwargs.get('executor_platform_id')

    headers = {'x-api-key': API_KEY}
    data = {'tasks': tasks, 'agent_id': agent_id,
            'executor_version_id': executor_version_id, 'executor_platform_id': executor_platform_id}
    r = requests.post(url=f'http://{API_HOST}:{API_PORT}/v2/agent/register', headers=headers, json=data)

    def on_failure(self, *args, **kwargs):
        pass

    return str(r.ok)


@celery_app.task(name='disjoin_group', track_started=True, default_retry_delay=2, max_retries=3, acks_late=True, bind=True)
def process_script(self, agent_id):
    headers = {'x-api-key': API_KEY}
    data = {'agent_id': agent_id}
    r = requests.post(url=f'http://{API_HOST}:{API_PORT}/v2/agent/unregister', headers=headers, json=data)

    def on_failure(self, *args, **kwargs):
        pass

    return str(r.ok)
