#!/bin/bash
# Source: https://github.com/node-red/node-red-docker/blob/master/docker-custom/scripts/entrypoint.sh

trap stop SIGINT SIGTERM

function stop() {
	kill $CHILD_PID
	wait $CHILD_PID
}

# Install missing modules
(cd /data && npm install)
echo "helloworld" 

/usr/local/bin/node $NODE_OPTIONS node_modules/node-red/red.js --userDir /data $FLOWS "${@}" &

CHILD_PID="$!"

wait "${CHILD_PID}"