![JE platform logo](/assets/logo.png)

Multipurpose jobs executor platform based on Celery. 
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

Jobs are executed by Celery *agents*. `startup-agent` is a convenient script to start an agent (inside the [worker](worker) folder): 

```console
# chmod +x startup-agent.sh
$ ./startup-agent.sh worker.web
```

## Generate documentation

Install APIDOC as follows:

```console
$ npm install apidoc -g
```

And then run:

```console
$ apidoc -i server/ -o server/doc
```
