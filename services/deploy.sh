#!/bin/bash
SCRIPTPATH="$( cd "$(dirname "$0")" >/dev/null 2>&1 ; pwd -P )"

# Copy the service into the systems services folder
# Inject path to executable
working_dir=$(realpath ../)
sed -e "s/\${working_dir}/$working_dir/" ${SCRIPTPATH}/mqtt-temp.service | sudo tee /etc/systemd/system/mqtt-sensors.service
