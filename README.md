![JE platform logo](/assets/logo.png)

Multipurpose jobs executor platform based on Celery. 
This repository provides core components of the platform, specifically:

* REST API for managing jobs and
* Agent (i.e., workers) for running jobs.

This project requires a running RabbitMQ broker and an instance of MongoDB to work. You can run RabbitMQ, MongoDB and Flower using Docker Compose:

```console
docker-compose up -d
``` 

To startup the server, run:

```console
# chmod +x startup-server.sh wait-for-it.sh
./startup-server.sh
```

## Agents

Jobs are executed by Celery workers which must be initialized first:

```console
# chmod +x startup-agent.sh wait-for-it.sh
./startup-agent.sh
```

## Run jobs

To execute several Python scripts inline, use the endpoint `/v2/run`:

```console
curl -X POST \
  http://localhost:6565/v2/run \
  -d '[{ "name":"say hello", "script":"print('\''hello'\'')"}, {"name":"print env", "script":"import os; print(os.environ['\''HOME'\''])"}]'
```

You can use the ticket id (`ticket_id`) provided in the response's body to check the status of a workflow:

```console
curl -X GET \
  'http://localhost:6565/v2/status?ticket_id=<ticket_id>'
```