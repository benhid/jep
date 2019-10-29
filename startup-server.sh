#!/bin/bash
set -e

export API_HOST=0.0.0.0
export API_PORT=6565
export API_KEY=CD3DC6F9EC4FCACB9A791CD7D43DD

export API_DB_HOST=${API_DB_HOST:-127.0.0.1}
export API_DB_PORT=${API_DB_PORT:-27017}
export API_DB_USERNAME=${API_DB_USERNAME:-root}
export API_DB_PASSWORD=${API_DB_PASSWORD:-root}

export CELERY_BROKER_HOST=${CELERY_BROKER_HOST:-127.0.0.1}
export CELERY_BROKER_PORT=${CELERY_BROKER_PORT:-5672}
export CELERY_BROKER_USERNAME=${CELERY_BROKER_USERNAME:-rabbit}
export CELERY_BROKER_PASSWORD=${CELERY_BROKER_PASSWORD:-rabbit}

export CELERY_DB_HOST=${CELERY_DB_HOST:-127.0.0.1}
export CELERY_DB_PORT=${CELERY_DB_PORT:-6379}
export CELERY_DB_USERNAME=${CELERY_DB_USERNAME:-redis}
export CELERY_DB_PASSWORD=${CELERY_DB_PASSWORD:-redis}

function capture ()
{
    echo [SERVER] Shutting down server...

    echo [SERVER] Shutting down agent server.manager...
    pkill -f "celery worker -A server.manager"

    echo [SERVER] Deleting server.manager.celeryd.pid file...
    rm -f ./server.manager.celeryd.pid

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
./wait-for-it.sh "${CELERY_BROKER_HOST}:${CELERY_BROKER_PORT}" -t 60
./wait-for-it.sh "${API_DB_HOST}:${API_DB_PORT}" -t 60

# start manager
echo [SERVER] Starting agent server.manager
celery worker \
    -A server.manager \
    -Q "events" \
    -n "server.manager" \
    --pidfile="./server.manager.celeryd.pid" \
    --loglevel=INFO \
    --logfile="./server.manager.celeryd.log" \
    --detach

# start server on init
echo [SERVER] Running server
python -m server.api
