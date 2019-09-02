#!/bin/bash
set -e

export API_HOST="192.168.48.222"
export API_PORT="6565"

export RABBIT_HOST=${RABBIT_HOST:-127.0.0.1}
export RABBIT_PORT=${RABBIT_PORT:-5672}
export RABBIT_USERNAME=${RABBIT_USERNAME:-rabbit}
export RABBIT_PASSWORD=${RABBIT_PASSWORD:-rabbit}

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
agent/wait-for-it.sh "${RABBIT_HOST}:${RABBIT_PORT}" -t 10

# start server on init
echo [SERVER] Running server
python -m server.api
