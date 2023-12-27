# Install the gpiod daemon 

More information on http://abyz.me.uk/rpi/pigpio/download.html or https://www.elektronik-kompendium.de/sites/raspberry-pi/2202121.htm

1. `sudo apt-get install pigpio`
2. Modify the pigpiod service to trust the remote control
    1. Run `sudo nano /lib/systemd/system/pigpiod.service`
    2. Change the `ExecStart` line to `ExecStart=/usr/bin/pigpiod -n localhost -n {ip-address}`. With `{ip-address}` being referring to the main controller.
    3. In section `[Service]` add the lines `Restart=always` and `RestartSec=5`
3. `sudo systemctl daemon-reload`
4. `sudo systemctl restart pigpiod`
5. `sudo systemctl enable pigpiod`
6. Enable remote gpiod with autostart `sudo systemctl enable pigpiod`