## Setup
1. Prepare 1-Wire Sensors
    1. Run `echo "dtoverlay=w1-gpio,gpiopin=4" | sudo tee -a /boot/config.txt` if not already contained in `/boot/config.txt` ([source](https://www.kompf.de/weather/pionewiremini.html))
    2. Reboot
    3. Check via `lsmod | grep w1`. Output should contain `w1_therm` and `w1_pgio`
2. Run `make setup` to install all dependencies

# Run
1. Run `make run` to launch node-red, mqtt, and pigpiod (for pin accessing)
2. Run `make help` to get a list of all available commands
