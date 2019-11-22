import time
import uuid
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
    route_name='workflow/run',
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
    @apiParam {json[]} body.jobs Jobs list
    @apiParam {String} body.jobs.task_name Task name (see: /v2/agents)
    @apiParam {Object} body.jobs.task_data Any necessary information to run the job
    @apiParam {json} body.jobs.meta (Optional) metadata of the job (such as description)
    @apiParam {json} body.meta (Optional) metadata to include in the ticket's body

    @apiParamExample {json} Request body example:
        {
            "jobs": [
                {
                    "task_name":"print",
                    "task_data":"required metadata to run the task",
                    "meta": {}
                }
            ],
            "meta": {}
        }

    @apiExample {curl} Example usage:
        curl -X POST \
            http://localhost:6565/v2/run \
            -H 'x-api-key: CD3DC6F9EC4FCACB9A791CD7D43DD' \
            -d '{ "jobs": [{"task_name":"run_script_py", "task_data":"import os; print(os.environ['\''HOME'\''])"}] }'

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
            "ticket_id": "46884-546541-1456",
            "created_on": 1571757474,
            "updated_on": null,
            "last_access": null,
            "process_chain_list": [
                {
                    "job_id": "226bcb1d-86f6-4948-93bc-8768bd075979",
                    "job_number": 0,
                    "task_name": "run_script_py",
                    "task_data": "ComponentReadCSV15717574740",
                    "executed_on": 1571757474.3573134,
                    "progress": {
                        "state": "PENDING",
                        "return": null
                    },
                    "metadata": {}
                }
            ],
            "progress": {
                "state": "PENDING",
                "num_of_steps": 1,
                "step": 0
            },
            "metadata": {}
        }

    @apiError InternalServerError Input request body does not match template
    """
    # get workflow
    workflow = request.json_body
    jobs = workflow['jobs']
    meta = workflow.get('meta', {})

    # get available tasks
    agents: dict = request.registry.agents
    available_tasks = sum(agents.values(), [])
    available_task_names = [t['name'] for t in available_tasks]

    # generate ticket
    ticket_id = str(uuid.uuid1())
    process_chain_list = []

    debug(f'new ticket id {ticket_id}')

    for idx, job in enumerate(jobs):
        try:
            task_name = job["task_name"]
            task_data = job["task_data"]
            job_meta = job.get('meta', {})
        except KeyError as e:
            raise HTTPBadRequest(f'key {e.args[0]} was not found')

        if task_name not in available_task_names:
            raise HTTPBadRequest(f'task {task_name} was not found (no worker available for given task)')

        debug(f'\trunning job {task_name}')

        task = celery_app.signature(
            task_name,
            kwargs={'data': task_data},
            queue='jobs'
        ).delay()

        debug('\tadding job to process chain list')

        process_chain_list.append({
            'job_id': str(task.task_id),
            'job_number': idx,
            'task_name': task_name,
            'task_data': task_data,
            'executed_on': time.time(),
            'progress': {
                'state': str(task.status),
                'return': str(task.result)
            },
            'metadata': job_meta
        })

    # compose ticket structure
    ticket = {
        'api_info': {'method': 'POST', 'endpoint': API_HOST, 'path': '/v2/run'},
        'ticket_id': ticket_id,
        'created_on': time.time(),
        'updated_on': time.time(),
        'last_access': None,
        'process_chain_list': process_chain_list,
        'progress': {
            'state': states.PENDING,
            'num_of_steps': len(jobs),  # total number of jobs
            'step': 0  # current job
        },
        'metadata': meta
    }

    # insert to database
    database = request.registry.database
    document = database.tickets.insert_one(ticket)

    debug(f'\tstored ticket {ticket_id} @ {document.inserted_id}')

    # serialize ObjectId
    ticket['_id'] = str(ticket['_id'])

    return ticket


@view_config(
    renderer='json',
    route_name='workflow/status',
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
                "path": "/v2/status"
            },
            "ticket_id": "46884-546541-1456",
            "created_on": 1571757474,
            "updated_on": 1564464481,
            "last_access": 1564464481,
            "process_chain_list": [
                {
                    "job_id": "226bcb1d-86f6-4948-93bc-8768bd075979",
                    "job_number": 0,
                    "task_name": "run_script_py",
                    "task_data": "ComponentReadCSV15717574740",
                    "executed_on": 1571757474.3573134,
                    "progress": {
                        "state": "SUCCESS",
                        "return": ""
                    },
                    "metadata": {}
                }
            ],
            "progress": {
                "state": "SUCCESS",
                "num_of_steps": 1,
                "step": 1
            },
            "metadata": {}
        }

    @apiError BadRequest Ticket identifier not found
    """
    # get ticket
    ticket_id = request.GET.get('ticket_id', None)
    debug(f'retrieving ticket id {ticket_id}')

    # find ticket by id
    database = request.registry.database
    ticket = database.tickets.find_one({'ticket_id': ticket_id})

    if ticket:
        # update API call info (only the first time by checking last_access)
        if not ticket['last_access']:
            ticket['api_info'] = {'method': 'GET', 'endpoint': API_HOST, 'path': '/v2/status'}

        # update times
        ticket['last_access'] = ticket['updated_on']
        ticket['updated_on'] = time.time()

        # we will only update still PENDING tickets
        if ticket['progress']['state'] == states.PENDING:
            # update progress of every job
            jobs = ticket['process_chain_list']
            step = 0

            for job in jobs:
                job_id = job['job_id']
                task = AsyncResult(job_id)

                try:
                    state = task.status
                    result = str(task.result)
                except ConnectionResetError:
                    raise

                # update state
                job['progress']['state'] = state

                # if finished (i.e., state is SUCCESS or FAILURE) increase step number and update return
                if state == states.SUCCESS or state == states.FAILURE:
                    job['progress']['return'] = result
                    step += 1

            # update current step number
            ticket['progress']['step'] = step

            # update ticket state if all jobs have finished
            if step == ticket['progress']['num_of_steps']:
                # if any job has state FAILURE, workflow status is also set to FAILURE; otherwise, SUCCESS
                if any(job['progress']['state'] == states.FAILURE for job in jobs):
                    ticket['progress']['state'] = states.FAILURE
                else:
                    ticket['progress']['state'] = states.SUCCESS

        # update ticket on database by replacing old values
        database.tickets.replace_one({'ticket_id': ticket_id}, ticket)
    else:
        raise HTTPBadRequest(f'ticket {ticket_id} not found')

    # serialize ObjectId (from mongodb)
    ticket['_id'] = str(ticket['_id'])

    return ticket


@view_config(
    renderer='json',
    route_name='job/check',
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
    route_name='job/kill',
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
    route_name='agents',
    request_method='GET'
)
def list_agents(request):
    """
    @api {get} /v2/agents List available agents
    @apiVersion 0.1.0
    @apiName GetAgents
    @apiGroup Agent
    @apiPermission none

    @apiExample {curl} Example usage:
        curl -X GET \
            http://localhost:6565/v2/agents

    @apiSuccess {json} body
    @apiSuccess {json[]} body.api_info Endpoint details
    @apiSuccess {json[]} body.agents List of available agents

    @apiSuccessExample {json} Success body example:
        HTTP/1.1 200 OK
        {
          "api_info": {
            "method": "GET",
            "endpoint": "0.0.0.0",
            "path": "/v2/agents"
          },
          "agents": {}
        }
    """
    agents: dict = request.registry.agents

    return {
        'api_info': {'method': 'GET', 'endpoint': API_HOST, 'path': '/v2/agents'},
        'tasks': sum(agents.values(), [])
    }


@view_config(
    renderer='json',
    route_name='agent/register',
    request_method='POST',
    decorator=requires_api_key
)
def register_agent(request):
    """
    @api {post} /v2/agent/register Register a new agent
    @apiVersion 0.1.0
    @apiName PostRegisterAgent
    @apiGroup Agent
    @apiPermission user

    @apiHeader {String} x-api-key API unique access-key
    @apiParam {json} body
    @apiParam {json} body.agent_id Unique agent identifier
    @apiParam {json[]} body.tasks Agent tasks

    @apiSuccess {json} body
    @apiSuccess {json} body.api_info Endpoint details
    @apiSuccess {String} body.agent_id Unique job identifier
    @apiSuccessExample {json} Success body example:
        HTTP/1.1 200 OK
        {
          "api_info": {
            "method": "POST",
            "endpoint": "0.0.0.0",
            "path": "/v2/agent/register "
          },
          "agent_id": "4581666186"
        }
    """
    agent = request.json_body
    agent_id = agent['agent_id']
    agent_tasks = agent['tasks']

    # register agent
    agents = request.registry.agents
    agents[agent_id] = agent_tasks

    return {
        'api_info': {'method': 'POST', 'endpoint': API_HOST, 'path': '/v2/agent/register'},
        'agent_id': agent['agent_id'],
    }


@view_config(
    renderer='json',
    route_name='agent/unregister',
    request_method='POST',
    decorator=requires_api_key
)
def unregister_agent(request):
    """
    @api {post} /v2/agent/unregister Un-register an agent
    @apiVersion 0.1.0
    @apiName PostUnRegisterAgent
    @apiGroup Agent
    @apiPermission user

    @apiHeader {String} x-api-key API unique access-key
    @apiParam {json} body
    @apiParam {json} body.agent_id Unique agent identifier

    @apiSuccess {json} body
    @apiSuccess {json} body.api_info Endpoint details
    @apiSuccess {String} body.agent_id Unique job identifier
    @apiSuccessExample {json} Success body example:
        HTTP/1.1 200 OK
        {
          "api_info": {
            "method": "POST",
            "endpoint": "0.0.0.0",
            "path": "/v2/agent/unregister "
          },
          "agent_id": "4581666186"
        }
    """
    agent = request.json_body
    agent_id = agent['agent_id']

    agents: dict = request.registry.agents

    try:
        del agents[agent_id]
    except KeyError:
        raise HTTPBadRequest(f'agent {agent_id} did not exists')

    return {
        'api_info': {'method': 'POST', 'endpoint': API_HOST, 'path': '/v2/agent/unregister'},
        'agent_id': agent['agent_id'],
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

        # add routes
        #  serve html (docs)
        config.add_static_view('docs', 'doc/', cache_max_age=3600)

        #  workflow
        config.add_route('workflow/run', '/v2/run')
        config.add_route('workflow/status', '/v2/status')

        #  jobs
        config.add_route('job/check', '/v2/check')
        config.add_route('job/kill', '/v2/kill')

        #  agents manager
        config.registry.agents = dict()

        config.add_route('agents', '/v2/agents')
        config.add_route('agent/register', '/v2/agent/register')
        config.add_route('agent/unregister', '/v2/agent/unregister')

        #  others
        config.add_route('health', '/v2/health')

        config.scan()

        # make WSGI
        app = config.make_wsgi_app()

    server = make_server(API_HOST, int(API_PORT), app)
    info(f'server at {API_HOST}:{API_PORT}')

    try:
        server.serve_forever()
    except KeyboardInterrupt:
        pass
