from celery.signals import worker_ready

from agent import celery_app


@worker_ready.connect
def register_agent(sender, **k):
    print('agent joined')


@celery_app.task(name='run_local_script', default_retry_delay=2, max_retries=3, acks_late=True, bind=True)
def process_script(self, msg):
    try:
        # we are making some assumptions here (such as the input script is SAFE to run)
        result = eval(msg)
    except Exception as e:
        result = e.__str__()
        raise Exception(result)

    def on_failure(self, *args, **kwargs):
        pass

    return result


@celery_app.task(name='run_local_file', default_retry_delay=2, max_retries=3, acks_late=True, bind=True)
def process_file(self, msg):
    pass
