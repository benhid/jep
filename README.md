![JE platform logo](/assets/logo.png)

Multipurpose jobs executor platform based on Celery. 
This repository provides core components of the platform, specifically:

* REST API for managing jobs and
* Agent (i.e., workers) for running jobs.

This project requires a running RabbitMQ broker and an instance of MongoDB and Redis to work. 
You can run RabbitMQ, MongoDB, Redis and Flower using Docker Compose:

```console
docker-compose up -d
``` 

To startup the server, run:

```console
# chmod +x startup-server.sh wait-for-it.sh
./startup-server.sh
```

## Agents

Jobs are executed by Celery workers. `startup-server` is a convenient script to start a worker within the [worker](worker) folder: 

```console
# chmod +x startup-agent.sh
./startup-agent.sh <filename_of_worker>
```

## Run jobs

To execute jobs, use the POST endpoint `/v2/run` with a body as follows:

```json
[
    {
        "task":"name_of_the_task",
        "name":"brief description or identifier of the task",
        "data":"required metadata to run the task"
    }
]
```

For example, the [executor](worker/executor.py) worker will be used to run Python scrips:

```console
./startup-agent.sh executor
```

Send a POST request to the `/v2/run` endpoint with the following body:

```console
curl -X POST \
  http://localhost:6565/v2/run \
  -H 'x-api-key: CD3DC6F9EC4FCACB9A791CD7D43DD' \
  -d '[{ "task":"run_script_py", "name":"say hello", "data":"print('\''hello'\'')"}, {"task":"run_script_py", "name":"print env", "data":"import os; print(os.environ['\''HOME'\''])"}]'
```

You can use the ticket id (`ticket_id`) provided in the response's body to check the status of a workflow:

```console
curl -X GET \
  'http://localhost:6565/v2/status?ticket_id=<ticket_id>'
```