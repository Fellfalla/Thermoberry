
#!/bin/bash
SCRIPTPATH="$( cd "$(dirname "$0")" >/dev/null 2>&1 ; pwd -P )"

# Copy the service into the systems services folder
# Inject path to executable
sensors_script=$(realpath ../sensors.py)
sudo sed -e "s/\${executable}/$sensors_script/" ${SCRIPTPATH}/mqtt-temp.service >> /etc/systemd/system/mqtt-sensors.service
