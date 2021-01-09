## Setup

1. Install the gpiod daemon http://abyz.me.uk/rpi/pigpio/download.html or https://www.elektronik-kompendium.de/sites/raspberry-pi/2202121.htm
    1. `sudo apt-get install pigpio`
    2. Modify the pigpiod service to trust the remote control
        1. Run `sudo nano /lib/systemd/system/pigpiod.service`
        2. Change the `ExecStart` line to `ExecStart=/usr/bin/pigpiod -n localhost -n {ip-address}`. With `{ip-address}` being referring to the main controller.
    3. `sudo systemctl daemon-reload`
    4. `sudo systemctl restart pigpiod`
    5. `sudo systemctl enable pigpiod`
2. Enable remote gpiod with autostart `sudo systemctl enable pigpiod`


### Enable Autostart
1. Run `bash services/mqtt-sensors.deploy.sh`

Note: Have a look at the status via `sudo systemctl status mqtt-sensors.service`n