#!/bin/bash
set -e

export API_HOST="0.0.0.0"
export API_PORT="6565"

export CELERY_BROKER_HOST=${CELERY_BROKER_HOST:-127.0.0.1}
export CELERY_BROKER_PORT=${CELERY_BROKER_PORT:-5672}
export CELERY_BROKER_USERNAME=${CELERY_BROKER_USERNAME:-rabbit}
export CELERY_BROKER_PASSWORD=${CELERY_BROKER_PASSWORD:-rabbit}

function capture ()
{
    echo [SERVER] Shutting down server...
    echo [SERVER] ...OK

    # exit shell script with error code 2
    # if omitted, shell script will continue execution
    exit 2
}

# initialise trap to call capture function
# when signal 2 (SIGINT) is received
trap "capture" 2

# wait for connection
echo [SERVER] Waiting for Rabbit instance
agent/wait-for-it.sh "${CELERY_BROKER_HOST}:${CELERY_BROKER_PORT}" -t 10

# start server on init
echo [SERVER] Running server
python -m server.api
