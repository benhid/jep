#!/bin/bash
set -e

export EXECUTOR_PLATFORM_ID="JEplatform"
export EXECUTOR_VERSION_ID="1.0"

export CELERY_BROKER_HOST=${CELERY_BROKER_HOST:-127.0.0.1}
export CELERY_BROKER_PORT=${CELERY_BROKER_PORT:-5672}
export CELERY_BROKER_USERNAME=${CELERY_BROKER_USERNAME:-rabbit}
export CELERY_BROKER_PASSWORD=${CELERY_BROKER_PASSWORD:-rabbit}

function capture ()
{
    echo [AGENT] Shutting down agent...
    pkill -f "celery worker -A worker.agent"

    echo [AGENT] Deleting celeryd.pid file...
    rm -f ./celeryd.pid

    echo [AGENT] ...OK

    # exit shell script with error code 2
    # if omitted, shell script will continue execution
    exit 2
}

# initialise trap to call capture function
# when signal 2 (SIGINT) is received
trap "capture" 2

# wait for connection
echo [AGENT] Waiting for Rabbit instance
./wait-for-it.sh "${CELERY_BROKER_HOST}:${CELERY_BROKER_PORT}" -t 60

# start worker on init
echo [AGENT] Starting agent
celery worker -A worker.agent -n "${EXECUTOR_PLATFORM_ID}-${EXECUTOR_VERSION_ID}" -Q "jobs" --loglevel=INFO --logfile="./agent.log" --detach

sleep 5

tail -f ./agent.log
