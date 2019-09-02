#!/bin/bash
set -e

export EXECUTOR_PLATFORM_ID="jobs"
export EXECUTOR_VERSION_ID="1"

export RABBIT_HOST="127.0.0.1"
export RABBIT_PORT="5672"
export RABBIT_USERNAME="rabbit"
export RABBIT_PASSWORD="rabbit"

# wait for connection
agent/wait-for-it.sh "127.0.0.1:5672" -t 60

# Start worker on init
celery worker -A agent.agent -Q "${EXECUTOR_PLATFORM_ID}-${EXECUTOR_VERSION_ID}" --loglevel=INFO --logfile="./agent.log" --detach

sleep 5

tail -f ./agent.log