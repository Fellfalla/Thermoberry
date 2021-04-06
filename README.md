## Setup

1. [Install Node-Red](https://nodered.org/docs/getting-started/raspberrypi)
    1. `bash <(curl -sL https://raw.githubusercontent.com/node-red/linux-installers/master/deb/update-nodejs-and-nodered)`
    2. Open the node-red browser interface `<ip-address>/:1880/` and install following packages:
        * node-red-contrib-ds18b20-sensor
        * node-red-dashboard
        * node-red-node-pi-gpio
        * node-red-node-pi-gpiod
    3.  Open the node-red browser interface `<ip-address>/:1880/` and import the [node red flow](node-red-flow.json)
1. Prepare Python3
    1. `sudo apt update && sudo apt install python3 python3-pip`
    2. `pip3 install -r requirements.txt`
2. [Install MQTT](https://www.vultr.com/docs/how-to-install-mosquitto-mqtt-broker-server-on-ubuntu-16-04):
    1. `sudo apt update && sudo apt install mosquitto mosquitto-clients`
3. Install the gpiod daemon http://abyz.me.uk/rpi/pigpio/download.html or https://www.elektronik-kompendium.de/sites/raspberry-pi/2202121.htm
    1. `sudo apt-get install pigpio`
    2. Modify the pigpiod service to trust the remote control
        1. Run `sudo nano /lib/systemd/system/pigpiod.service`
        2. Change the `ExecStart` line to `ExecStart=/usr/bin/pigpiod -n localhost -n {ip-address}`. With `{ip-address}` being referring to the main controller.
    3. `sudo systemctl daemon-reload`
    4. `sudo systemctl restart pigpiod`
    5. `sudo systemctl enable pigpiod`
    6. Enable remote gpiod with autostart `sudo systemctl enable pigpiod`


### Enable Autostart
1. Follow instructions in [services](services/README.md) to deploy custom services
2. Node-Red: `sudo systemctl enable nodered.service`

Note: Have a look at the status via `systemctl status thermoberry-sensors.service`