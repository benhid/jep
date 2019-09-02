# JE platform 💀

Multipurpose jobs executor platform based on Celery. 
This repository provides core components of the platform, specifically:

* REST API for managing jobs and
* Agent (i.e., workers) for running jobs.

## Agents

Jobs are executed by Celery workers which must be initialized first:

```console
# chmod +x agent/startup-agent.sh agent/wait-for-it.sh
agent/startup-agent.sh
```

