#!/bin/bash
set -e

export EXECUTOR_PLATFORM_ID="JEplatform"
export EXECUTOR_VERSION_ID="1.0"

export CELERY_BROKER_HOST=${CELERY_BROKER_HOST:-127.0.0.1}
export CELERY_BROKER_PORT=${CELERY_BROKER_PORT:-5672}
export CELERY_BROKER_USERNAME=${CELERY_BROKER_USERNAME:-rabbit}
export CELERY_BROKER_PASSWORD=${CELERY_BROKER_PASSWORD:-rabbit}

export CELERY_DB_HOST=${CELERY_DB_HOST:-127.0.0.1}
export CELERY_DB_PORT=${CELERY_DB_PORT:-6379}
export CELERY_DB_USERNAME=${CELERY_DB_USERNAME:-redis}
export CELERY_DB_PASSWORD=${CELERY_DB_PASSWORD:-redis}

AGENT_NAME="$1"

# check if file exists
if [ ! -f "./worker/${AGENT_NAME}.py" ]; then
    echo "[AGENT] Agent ${AGENT_NAME} was not found inside /worker"
    exit 1
fi

function capture ()
{
    echo [AGENT] Shutting down agent "$AGENT_NAME"...
    pkill -f "celery worker -A worker.${AGENT_NAME}"

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
./wait-for-it.sh "${CELERY_DB_HOST}:${CELERY_DB_PORT}" -t 60

# start worker on init
echo [AGENT] Starting agent "$AGENT_NAME"
celery worker -A worker."$AGENT_NAME" -n "${EXECUTOR_PLATFORM_ID}-${EXECUTOR_VERSION_ID}" -Q "jobs" --loglevel=INFO --logfile="./${AGENT_NAME}-agent.log" --detach

sleep 5

tail -f ./${AGENT_NAME}-agent.log
