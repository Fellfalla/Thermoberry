#!/bin/bash

Help()
{
   # Display Help
   echo "Helper script to deploy (install and enable) a given service."
   echo
   echo "Syntax: deploy-service.sh [srv1 srv2 ...]"
   echo
}

if [ $# -eq 0 ] ; then
    Help
    exit 1
fi

SCRIPTPATH="$( cd "$(dirname "$0")" >/dev/null 2>&1 ; pwd -P )"

for srv in "$@"
do
    echo "Deploying " $srv
    echo "$var"

    # Copy the service into the systems services folder
    # Inject path to executable
    working_dir=$(realpath $SCRIPTPATH/..)
    sed -e "s+\${working_dir}+$working_dir+" $srv | sudo tee /etc/systemd/system/$(basename $srv)

    # Update the systemctl files
    sudo systemctl daemon-reload

    # Run the service
    sudo systemctl restart $(basename $srv)

    # Enable autostart
    sudo systemctl enable $(basename $srv)

    # to remove from autostart: sudo systemctl disable mqtt-sensors.service
done
