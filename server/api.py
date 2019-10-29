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
from server.security import requires_api_key


@view_config(
    renderer='json',
    route_name='run',
    request_method='POST',
    decorator=requires_api_key
)
def issue_ticket(request):
    """
    @api {post} /v2/run Issue new ticket
    @apiVersion 0.1.0
    @apiName PostTicket
    @apiGroup Ticket
    @apiPermission user

    @apiHeader {String} x-api-key API unique access-key
    @apiParam {json} body
    @apiParam {json} body.meta (Optional) metadata to include in the ticket's body
    @apiParam {json[]} body.jobs Jobs list
    @apiParam {String} body.jobs.task Job code
    @apiParam {String} body.jobs.name Name/description of the job
    @apiParam {String} body.jobs.data Any necessary data to run the job

    @apiParamExample {json} Request body example:
        {
            meta: {},
            jobs: [
                {
                    "task":"name_of_the_task",
                    "name":"brief description or identifier of the task",
                    "data":"required metadata to run the task"
                }
            ]
        }

    @apiExample {curl} Example usage:
        curl -X POST \
            http://localhost:6565/v2/run \
            -H 'x-api-key: CD3DC6F9EC4FCACB9A791CD7D43DD' \
            -d '{ "jobs": [{"task":"run_script_py", "name":"print env", "data":"import os; print(os.environ['\''HOME'\''])"}], "meta": {} }'

    @apiSuccess {json} body
    @apiSuccess {json[]} body.api_info Endpoint details
    @apiSuccess {String} body.ticket_id Unique ticket identifier
    @apiSuccess {Date} body.created_on Ticket creation date
    @apiSuccess {Date} body.updated_on
    @apiSuccess {Date} body.last_access Last ticket's access date
    @apiSuccess {json} body.metadata Input metadata from request body
    @apiSuccess {json[]} body.process_chain_list Jobs chain list
    @apiSuccess {json} body.progress Ticket progress
    @apiSuccess {String} body.progress.state Ticket global state
    @apiSuccess {Integer} body.progress.num_of_steps Number of total steps (i.e., jobs)
    @apiSuccess {Integer} body.progress.step Current executing job

    @apiSuccessExample {json} Success body example:
        HTTP/1.1 200 OK
        {
          "_id": "5daf1da2a9f541a00597db3a",
          "api_info": {
            "method": "GET",
            "endpoint": "0.0.0.0",
            "path": "/v2/run"
          },
          "created_on": 1571757474,
          "updated_on": null,
          "last_access": null,
          "ticket_id": "1571757474",
          "metadata": {},
          "process_chain_list": [
            {
              "job_id": "226bcb1d-86f6-4948-93bc-8768bd075979",
              "job_code": "run_script_py",
              "job_name": "ComponentReadCSV15717574740",
              "job_number": 0,
              "executed_on": 1571757474.3573134,
              "progress": {
                "state": "PENDING",
                "return": null
              }
            }
          ],
          "progress": {
            "state": "PENDING",
            "num_of_steps": 2,
            "step": 0
          }
        }

    @apiError InternalServerError Input request body does not match template
    """

    workflow = request.json_body
    ticket_id = str(int(time.time()))
    process_chain_list = []

    debug(f'new ticket id {ticket_id}')

    jobs = workflow['jobs']
    meta = workflow.get('meta', None)

    for idx, job in enumerate(jobs):
        try:
            job_code = job["task"]
            job_name = job["name"]
            job_data = job["data"]
        except Exception:
            raise

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
            'progress':{
                'state': str(task.status),
                'return': str(task.result)
            }
        })

    ticket = {
        'api_info': {'method': 'POST', 'endpoint': API_HOST, 'path': '/v2/run'},
        'created_on': time.time(),
        'updated_on': time.time(),
        'last_access': None,
        'ticket_id': ticket_id,
        'metadata': meta,
        'process_chain_list': process_chain_list,
        'progress': {
            'state': states.PENDING,
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
    @api {get} /v2/status Ticket execution state
    @apiVersion 0.1.0
    @apiName GetTicket
    @apiGroup Ticket
    @apiPermission none

    @apiParam {String} ticket_id Unique ticket identifier

    @apiExample {curl} Example usage:
        curl -X GET \
            http://localhost:6565/v2/status?ticket_id=<ticket_id>

    @apiSuccess {json} body
    @apiSuccess {json[]} body.api_info Unique ticket identifier
    @apiSuccess {String} body.ticket_id Unique ticket identifier
    @apiSuccess {Date} body.created_on Ticket creation date
    @apiSuccess {Date} body.updated_on 
    @apiSuccess {Date} body.last_access Last ticket's access date
    @apiSuccess {json} body.metadata Input metadata from request body
    @apiSuccess {json[]} body.process_chain_list Jobs chain list
    @apiSuccess {json} body.progress Ticket progress
    @apiSuccess {String} body.progress.state Ticket global state
    @apiSuccess {Integer} body.progress.num_of_steps Number of total steps (i.e., jobs)
    @apiSuccess {Integer} body.progress.step Current executing job

    @apiSuccessExample {json} Success body example:
        HTTP/1.1 200 OK
        {
          "_id": "5daf1da2a9f541a00597db3a",
          "api_info": {
            "method": "GET",
            "endpoint": "0.0.0.0",
            "path": "/v2/status"
          },
          "created_on": 1571757474,
          "updated_on": 1685247244,
          "last_access": 1685247244,
          "ticket_id": "1571757474",
          "metadata": {},
          "process_chain_list": [
            {
              "job_id": "226bcb1d-86f6-4948-93bc-8768bd075979",
              "job_code": "run_script_py",
              "job_name": "ComponentReadCSV15717574740",
              "job_number": 0,
              "executed_on": 1571757474.3573134,
              "progress": {
                "state": "SUCCESS",
                "return": "result"
              }
            }
          ],
          "progress": {
            "state": "SUCCESS",
            "num_of_steps": 2,
            "step": 2
          }
        }

    @apiError BadRequest Ticket identifier not found
    """
    ticket_id = request.GET.get('ticket_id', None)
    debug(f'retrieving ticket id {ticket_id}')

    # find ticket by id
    database = request.registry.database
    ticket = database.tickets.find_one({'ticket_id': ticket_id})

    if ticket:
        # update times
        ticket['last_access'] = ticket['updated_on']
        ticket['updated_on'] = time.time()

        # update API call info
        ticket['api_info'] = {'method': 'GET', 'endpoint': API_HOST, 'path': '/v2/status'}

        # update progress of every job
        jobs = ticket['process_chain_list']
        step = 0

        for job in jobs:
            id = job['job_id']
            task = AsyncResult(id)

            try:
                result = str(task.result)
                state = task.status
            except ConnectionResetError:
                raise

            job['progress']['state'] = state

            # if finished, increase step number and return result
            if state == states.SUCCESS or state == states.FAILURE:
                job['progress']['return'] = result
                step += 1

        # set current step number
        ticket['progress']['step'] = step

        # update ticket state
        if step == ticket['progress']['num_of_steps']:
            # if any job is failing, workflow status is FAILURE; otherwise, SUCCESS
            if any(job['progress']['state'] == states.FAILURE for job in jobs):
                ticket['progress']['state'] = states.FAILURE
            else:
                ticket['progress']['state'] = states.SUCCESS

        # update ticket on database
        database.tickets.replace_one({'ticket_id': ticket_id}, ticket)
    else:
        raise HTTPBadRequest(f'ticket {ticket_id} not found')

    # serialize ObjectId (from mongodb)
    ticket['_id'] = str(ticket['_id'])

    return ticket


@view_config(
    renderer='json',
    route_name='check',
    request_method='GET'
)
def check_job(request):
    """
    @api {get} /v2/check Job execution state
    @apiVersion 0.1.0
    @apiName GetJob
    @apiGroup Job
    @apiPermission none

    @apiParam {String} job_id Unique job identifier

    @apiExample {curl} Example usage:
        curl -X GET \
            http://localhost:6565/v2/check?job_id=<job_id>

    @apiSuccess {json} body
    @apiSuccess {json[]} body.api_info Endpoint details
    @apiSuccess {Integer} body.job_id Unique job identifier
    @apiSuccess {json} body.progress Job progress
    @apiSuccess {String} body.progress.state Job execution status
    @apiSuccess {String} body.progress.return Job results (if any)

    @apiSuccessExample {json} Success body example:
        HTTP/1.1 200 OK
        {
          "api_info": {
            "method": "GET",
            "endpoint": "0.0.0.0",
            "path": "/v2/check"
          },
          "job_id": 4581666186,
          "progress": {
            "state": "SUCCESS",
            "return": ""
          }
        }
    """
    job_id = request.GET.get('job_id', '0')
    task = AsyncResult(job_id)

    try:
        result = str(task.result)
        state = task.status
    except ConnectionResetError:
        raise

    return {
        'api_info': {'method': 'GET', 'endpoint': API_HOST, 'path': '/v2/check'},
        'job_id': job_id,
        'progress': {
            'state': state,
            'return': result
        }
    }


@view_config(
    renderer='json',
    route_name='kill',
    request_method='POST',
    decorator=requires_api_key
)
def kill_job(request):
    """
    @api {post} /v2/kill Kill running job
    @apiVersion 0.1.0
    @apiName PostJob
    @apiGroup Job
    @apiPermission user

    @apiHeader {String} x-api-key API unique access-key
    @apiParam {json} body
    @apiParam {json} body.job_id Unique job identifier

    @apiParamExample {json} Request body example:
        {
            "job_id": "4581666186"
        }

    @apiSuccess {json} body
    @apiSuccess {json} body.api_info Endpoint details
    @apiSuccess {Integer} body.job_id Unique job identifier
    @apiSuccess {json} body.progress Job progress
    @apiSuccess {String} body.progress.state Job execution status
    @apiSuccess {String} body.progress.return Job result (i.e., None)

    @apiSuccessExample {json} Success body example:
        HTTP/1.1 200 OK
        {
          "api_info": {
            "method": "POST",
            "endpoint": "0.0.0.0",
            "path": "/v2/kill"
          },
          "job_id": 4581666186,
          "progress": {
            "state": "REVOKED",
            "return": null
          }
        }
    """
    job_id = request.json_body.get('job_id', None)
    result = AsyncResult(job_id)

    result.revoke(terminate=True)

    return {
        'api_info': {'method': 'POST', 'endpoint': API_HOST, 'path': '/v2/kill'},
        'job_id': job_id,
        'progress': {
            'state': states.REVOKED,
            'result': None
        }
    }


@view_config(
    renderer='json',
    route_name='health',
    request_method='GET'
)
def health(request):
    """
    @api {post} /v2/health Check API status
    @apiVersion 0.1.0
    @apiName GetHealth
    @apiGroup System
    @apiPermission none

    @apiSuccessExample {http} Success body example:
        HTTP/1.1 200 OK
    """
    return Response(status=200)


@notfound_view_config()
def notfound(request):
    return Response('Resource not Found', status='404')


if __name__ == '__main__':
    client = MongoClient(f'mongodb://{API_DB_USERNAME}:{API_DB_PASSWORD}@{API_DB_HOST}:{API_DB_PORT}/')

    with Configurator() as config:
        config.include('server.cors')

        # register database
        config.registry.database = client['je-database']

        # serve html
        config.add_static_view('docs', 'doc/', cache_max_age=3600)

        # add routes
        config.add_route('run', '/v2/run')
        config.add_route('status', '/v2/status')
        config.add_route('check', '/v2/check')
        config.add_route('kill', '/v2/kill')
        config.add_route('health', '/v2/health')

        config.scan()

        app = config.make_wsgi_app()

    server = make_server(API_HOST, int(API_PORT), app)
    info(f'server at {API_HOST}:{API_PORT}')

    try:
        server.serve_forever()
    except KeyboardInterrupt:
        pass
