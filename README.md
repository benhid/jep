![JE platform logo](/assets/logo.png)

Multipurpose jobs executor platform based on Celery. 
This repository provides core components of the platform, specifically:

* REST API for managing jobs and
* Agent (i.e., workers) for running jobs.

This project requires a running RabbitMQ broker and an instance of MongoDB and Redis to work. 
You can run RabbitMQ, MongoDB, Redis and Flower using Docker Compose:

```console
$ docker-compose up -d
``` 

To startup the server, run:

```console
# chmod +x startup-server.sh wait-for-it.sh
$ ./startup-server.sh
```

## Agents

Jobs are executed by Celery workers. `startup-server` is a convenient script to start a worker within the [worker](worker) folder: 

```console
# chmod +x startup-agent.sh
$ ./startup-agent.sh <filename_of_worker>
```

## Run jobs

To execute jobs, use the POST endpoint `/v2/run` with a body as follows:

```json
[
    {
        "task":"task id",
        "name":"brief description or identifier of the job",
        "data":"required metadata to run the task"
    }
]
```

## Generate documentation

Install APIDOC as follows:

```console
$ npm install apidoc -g
```

And then run:

```console
$ apidoc -i server/ -o /server/doc
```
