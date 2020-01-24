![JEPlatform logo](/assets/logo.png)

Multipurpose **j**obs **e**xecutor **p**latform based on Celery. 
This repository provides core components of the platform, specifically:

* REST API for managing jobs and
* Agents for running jobs.

This project requires a running RabbitMQ broker and an instance of MongoDB and Redis to work. 
You can run RabbitMQ, MongoDB, Redis and Flower using Docker Compose:

```console
$ docker-compose up -d
``` 

#### Server 

To startup the server, run:

```console
# chmod +x startup-server.sh wait-for-it.sh
$ ./startup-server.sh
```

#### Agents

Jobs are executed by Celery *agents*. `startup-agent` is a convenient script to start an agent: 

```console
# chmod +x startup-agent.sh
$ ./startup-agent.sh worker.web
```

**Note** Sometimes, Celery worker may be working on the background after its shutdown and generate zombie processes.
Use `pkill -f "celery worker"` to stop all running workers.

## Generate documentation

Install APIDOC as follows:

```console
$ npm install apidoc -g
```

And then run:

```console
$ apidoc -i server/ -o server/doc
```
