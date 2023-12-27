# Install Node-Red

More information on [Install Node-Red](https://nodered.org/docs/getting-started/raspberrypi)

1. `bash <(curl -sL https://raw.githubusercontent.com/node-red/linux-installers/master/deb/update-nodejs-and-nodered)`
2. Open the node-red browser interface `<ip-address>/:1880/` and install following packages:
    * node-red-contrib-ds18b20-sensor
    * node-red-dashboard
    * node-red-node-pi-gpio
    * node-red-node-pi-gpiod
3.  Open the node-red browser interface `<ip-address>/:1880/` and import the [node red flow](node-red-flow.json)


### Enable Autostart
1. Node-Red: `sudo systemctl enable nodered.service`