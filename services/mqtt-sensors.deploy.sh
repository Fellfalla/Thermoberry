#!/bin/bash
SCRIPTPATH="$( cd "$(dirname "$0")" >/dev/null 2>&1 ; pwd -P )"

# Copy the service into the systems services folder
# Inject path to executable
working_dir=$(realpath $SCRIPTPATH/..)
sed -e "s+\${working_dir}+$working_dir+" ${SCRIPTPATH}/mqtt-sensors.service | sudo tee /etc/systemd/system/mqtt-sensors.service

# Update the systemctl files
sudo systemctl daemon-reload

# Run the service
sudo systemctl start mqtt-sensors.service

# Enable autostart
sudo systemctl enable mqtt-sensors.service

# to remove from autostart: sudo systemctl disable mqtt-sensors.service