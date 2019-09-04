import time
from wsgiref.simple_server import make_server
from celery import states

from celery.result import AsyncResult
from pymongo import MongoClient
from pyramid.config import Configurator
from pyramid.httpexceptions import HTTPBadRequest
from pyramid.response import Response
from pyramid.view import notfound_view_config
from pyramid.view import view_config

from server import *


@view_config(
    renderer='json',
    route_name='run',
    request_method='POST'
)
def issue_ticket(request):
    jobs = request.json_body
    ticket_id = str(int(time.time()))
    process_chain_list = []

    debug(f'ticket id {ticket_id}')

    for idx, job in enumerate(jobs):
        job_code = job["task"]
        job_name = job["name"]
        job_data = job["data"]

        debug(f'\trunning job {job_name}')

        task = celery_app.signature(
            job_code,
            kwargs={'data': job_data},
            queue='jobs'
        ).delay()

        debug('\tadding job to process chain list')

        process_chain_list.append({
            'job_id': str(task.task_id),
            'job_code': job_code,
            'job_name': job_name,
            'job_number': idx,
            'executed_on': time.time(),
            'state': str(task.status),
            'return': str(task.result)
        })

    ticket = {
        'api_info': {'method': 'POST', 'endpoint': API_HOST, 'path': '/v2/run'},
        'created_on': time.time(),
        'updated_on': time.time(),
        'last_access': None,
        'ticket_id': ticket_id,
        'description': jobs,
        'state': states.PENDING,
        'process_chain_list': process_chain_list,
        'progress': {
            'num_of_steps': len(jobs),  # total number of jobs
            'step': 0  # current job
        }
    }

    # insert to database
    database = request.registry.database
    document = database.tickets.insert_one(ticket)

    debug(f'\tstored ticket {document.inserted_id}')

    # serialize ObjectId
    ticket['_id'] = str(ticket['_id'])

    return ticket


@view_config(
    renderer='json',
    route_name='status',
    request_method='GET'
)
def check_ticket(request):
    """
    Return global execution state.
    """
    ticket_id = request.GET.get('ticket_id', None)
    debug(f'retrieving ticket id {ticket_id}')

    # find by id
    database = request.registry.database
    ticket = database.tickets.find_one({'ticket_id': ticket_id})

    if ticket:
        # update times
        ticket['last_access'] = ticket['updated_on']
        ticket['updated_on'] = time.time()

        # update API info
        ticket['api_info'] = {'method': 'GET', 'endpoint': API_HOST, 'path': '/v2/status'}

        # update progress
        jobs = ticket['process_chain_list']
        step = 0

        for job in jobs:
            id = job['job_id']
            task = AsyncResult(id)

            try:
                result = task.result
                state = task.status
            except ConnectionResetError:
                raise

            job['state'] = state

            if state == states.SUCCESS or state == states.FAILURE:
                job['return'] = result
                step += 1

        # set current step number
        ticket['progress']['step'] = step

        if step == ticket['progress']['num_of_steps']:
            if any(job['state'] == states.FAILURE for job in jobs):
                ticket['state'] = states.FAILURE
            else:
                ticket['state'] = states.SUCCESS

        database.tickets.replace_one({'ticket_id': ticket_id}, ticket)
    else:
        raise HTTPBadRequest(f'ticket {ticket_id} not found')

    # serialize ObjectId
    ticket['_id'] = str(ticket['_id'])

    return ticket


@view_config(
    renderer='json',
    route_name='check',
    request_method='GET'
)
def check_job(request):
    """
    Return job execution state.
    """
    job_id = request.GET.get('job_id', '0')
    result = AsyncResult(job_id)

    return {
        'api_info': {'method': 'GET', 'endpoint': API_HOST, 'path': '/v2/check'},
        'job_id': job_id,
        'status': str(result.state),
        'return': str(result.result)
    }


@view_config(
    renderer='json',
    route_name='kill',
    request_method='POST'
)
def kill_job(request):
    """
    Terminate running job.
    """
    job_id = request.json_body.get('job_id', None)
    result = AsyncResult(job_id)

    result.revoke(terminate=True)

    return {
        'api_info': {'method': 'POST', 'endpoint': API_HOST, 'path': '/v2/kill'},
        'job_id': job_id,
        'status': 'REVOKED',
        'result': None
    }


@notfound_view_config()
def notfound(request):
    return Response('Resource not Found', status='404')


if __name__ == '__main__':
    client = MongoClient(f'mongodb://{API_DB_USERNAME}:{API_DB_PASSWORD}@{API_DB_HOST}:{API_DB_PORT}/')

    with Configurator() as config:
        config.include('server.cors')

        # register database
        config.registry.database = client['je-database']

        # add routes
        config.add_route('run', '/v2/run')
        config.add_route('status', '/v2/status')
        config.add_route('check', '/v2/check')
        config.add_route('kill', '/v2/kill')
        config.scan()

        app = config.make_wsgi_app()

    try:
        server = make_server(API_HOST, int(API_PORT), app)
        server.serve_forever()
    except KeyboardInterrupt:
        pass
