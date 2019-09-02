import time
from wsgiref.simple_server import make_server

from celery.result import AsyncResult
from pyramid.config import Configurator
from pyramid.httpexceptions import HTTPBadRequest
from pyramid.response import Response
from pyramid.view import notfound_view_config
from pyramid.view import view_config
from tinydb import TinyDB, Query

from server import *


@view_config(
    route_name='run',
    renderer='json',
    request_method='POST'
)
def issue_ticket(request):
    jobs = request.json_body
    ticket_id = str(int(time.time()))
    process_chain_list = []

    debug(f'ticket id {ticket_id}')

    for idx, job in enumerate(jobs):
        debug(f'\trunning job {job["name"]}')

        run_local_script = celery_app.signature(
            'run_local_script',
            kwargs={'msg': job['script']},
            queue='jobs-1'
        ).delay()

        debug('\tadding job to process chain list')

        process_chain_list.append({
            'job_id': str(run_local_script.job_id),
            'job_name': job['name'],
            'job_number': idx,
            'executed_on': time.time(),
            'status': run_local_script.status,
            'return': str(run_local_script.result),
            'type': 'text'
        })

    ticket = {
        'api_info': {'method': 'POST', 'endpoint': API_HOST, 'path': '/v2/run'},
        'created_on': time.time(),
        'updated_on': time.time(),
        'ticket_id': ticket_id,
        'description': jobs,
        'status': 'PENDING',
        'priority': 'LOW',
        'process_chain_list': process_chain_list,
        'progress': {
            'num_of_steps': len(jobs),  # total number of jobs
            'step': 0  # current job
        }
    }

    # insert to database
    debug('\tinserting ticket to db')
    request.registry.db.insert(ticket)

    return ticket


@view_config(
    route_name='status',
    renderer='json',
    request_method='GET'
)
def check_ticket(request):
    """
    Return global execution state.
    """
    ticket_id = request.GET.get('ticket_id', None)
    debug(f'retrieving ticket id {ticket_id}')

    q = Query()
    ticket = request.registry.db.get(q.ticket_id == ticket_id)

    if ticket:
        step = 0

        for job in ticket['process_chain_list']:
            job_id = job['job_id']
            result = AsyncResult(job_id)

            try:
                job['status'] = str(result.state)
            except ConnectionResetError as e:
                raise e

            if result.status == 'SUCCESS' or result.status == 'FAILURE':
                job['return'] = str(result.result)

            if result.state != 'PENDING':
                step += 1

        ticket['updated_on'] = time.time()
        ticket['progress']['step'] = step

        if step == ticket['progress']['num_of_steps']:
            if any(operator['status'] == 'FAILURE' for operator in ticket['process_chain_list']):
                ticket['status'] = 'FAILURE'
            else:
                ticket['status'] = 'SUCCESS'

        request.registry.db.write_back([ticket])
    else:
        raise HTTPBadRequest(f'ticket {ticket_id} not found')

    return ticket


@view_config(
    route_name='check',
    renderer='json',
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
    route_name='kill',
    renderer='json',
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
    database = TinyDB('./tickets.json')

    with Configurator() as config:
        config.include('cors')

        # register database
        config.registry.db = database

        # add routes
        config.add_route('run', '/v2/run')
        config.add_route('status', '/v2/status')
        config.add_route('check', '/v2/check')
        config.add_route('kill', '/v2/kill')
        config.scan()

        app = config.make_wsgi_app()

    server = make_server(API_HOST, API_PORT, app)
    server.serve_forever()
