## Setup

1. Install the gpiod daemon http://abyz.me.uk/rpi/pigpio/download.html or https://www.elektronik-kompendium.de/sites/raspberry-pi/2202121.htm
    1. `sudo apt-get install pigpio`
    2. `sudo systemctl start pigpiod`
    3. `sudo systemctl enable pigpiod`
    4. Trust the main raspberry via `sudo pigpiod -n {ip-address}`
2. Enable remote gpiod with autostart `sudo systemctl enable pigpiod`


### Enable Autostart
1. Run `bash services/mqtt-sensors.deploy.sh`

Note: Have a look at the status via `sudo systemctl status mqtt-sensors.service`n