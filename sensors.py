#!/usr/bin/env python3
#Source: https://www.earth.li/~noodles/blog/2018/05/rpi-mqtt-temp.html

import os
import glob
import time
import subprocess
import socket
import logging
import json

# 3rd party libraries
import paho.mqtt.client as paho
import hydra
from omegaconf import DictConfig

# Local files
from module import Module
import utils

# Global variables
module_name = "Sensors"
logger = logging.getLogger(module_name)
machine = socket.gethostname()

def read_temp(sensor_dir, device_id):
    """
    Returns
        <float> temperature in [°C]
        <bool> valid_crc True if CRC check of reading is valid
    """
    valid_crc = False
    temp = 0

    measurement_path = os.path.join(sensor_dir, device_id, 'w1_slave')
    with open(measurement_path , 'r') as f:
        for line in f:
            if line.strip()[-3:] == 'YES':
                valid_crc = True
            temp_pos = line.find(' t=')
            if temp_pos != -1:
                temp = float(line[temp_pos + 3:]) / 1000.0

    return temp, valid_crc


class SensorModule(Module):
    def __init__(self, module_name):
        super().__init__(module_name=module_name)
        self.mixers = []

    def _connect(self, cfg):
        # Read the config
        self.sensor_dir = cfg.sensors.sensor_dir
        self.sensor_id_mapping = cfg.sensors.mapping
        self.reduction_factor = cfg.sensors.reduction_factor
        self.loop_timeout = cfg.sensors.loop_timeout

        # Initialize variables
        self.reduction_counter = 0

    def _loop(self):
        self.reduction_counter += 1

        # Retrieve a new list of devices every iteration to allow plug and play
        device_ids = [os.path.basename(x) for x in glob.glob(os.path.join(self.sensor_dir, '28-*'))]
        
        for device_id in device_ids:

            # 1. Read the Temperature
            logger.debug("Reading device %s"%(device_id))
            try:
                temp, is_valid = read_temp(sensor_dir, device_id)

                if not is_valid:
                    logger.error("Invalid CRC check for sensor %s"%(device_id))
                    continue

            except FileNotFoundError as e:
                # We lost the sensor
                logger.error("Sensor %s: %s"%(device_id, e.msg))
                continue

            # 2. Notify about missing information
            if device_id not in self.sensor_id_mapping:
                logger.warning(("No mapping found for %s"%(device_id)))
                sensor_name = device_id
            else:
                sensor_name = self.sensor_id_mapping[device_id]

            # 3. Notify the world about our nice temperature
            _ = self.mqtt_client.publish(sensor_name, payload=temp, qos=0, retain=False)

            if self.reduction_counter > self.reduction_factor:
                self.reduction_counter = 0
                reduced_topic = os.path.join("reduced", sensor_name)
                self.mqtt_client.publish(reduced_topic, payload=temp, qos=0, retain=False)

            
    def _disconnect(self):
        # Simple cleanup
        pass


@hydra.main(config_path="conf/config.yaml")
def main(cfg):
    # Prepare logging
    new_log_level = cfg.logging.level
    logger.info("Setting loglevel to %s"%(str(new_log_level)))
    logger.setLevel(new_log_level)

    try: 
        print("##### Start Measurement #####")
        sm = SensorModule(module_name)
        sm.connect(cfg)
        logger.info("Run measurement loop")
        sm.loop() # Run the measurement and publishing loop 
    except KeyboardInterrupt:
        print("##### Shutdown #####")
        pass
    except Exception as e:
        logger.exception(e)
        raise e


if __name__ == "__main__":
    main()
