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

@hydra.main(config_path="conf/config.yaml")
def measurement_loop(cfg):
    # Read the config
    sensor_dir = cfg.sensors.sensor_dir
    sensor_id_mapping = cfg.sensors.mapping

    # Prepare logging
    logger.info("Configure logging")
    new_log_level = cfg.logging.level
    logger.info("Setting loglevel to %s"%(str(new_log_level)))
    logger.setLevel(new_log_level)

    # Connect to MQTT broker
    logger.info("Connecting to MQTT broker...")
    mqtt_client = utils.create_mqtt_client(client_id="%s@%s"%(module_name, machine), clean_session=True, **cfg.mqtt)

    if mqtt_client:
        logger.info("Connection to MQTT broker: OK")
    else:
        logger.error("Connection to MQTT broker: FAILED")
        return

    # Run the measurement and publishing loop 
    logger.info("Run measurement loop")

    heartbeat_topic = machine + "/modules/" + module_name
    # TODO: move will_set before connect, otherwise it won't have any effect
    mqtt_client.publish(heartbeat_topic, payload=json.dumps(True), qos=2, retain=True) # Show that we are alive
    mqtt_client.will_set(heartbeat_topic, payload=json.dumps(False), qos=2, retain=True)

    while True:

        # Retrieve a new list of devices every iteration to allow plug and play
        device_ids = [os.path.basename(x) for x in glob.glob(os.path.join(sensor_dir, '28-*'))]

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
            if device_id not in sensor_id_mapping:
                logger.warning(("No mapping found for %s"%(device_id)))
                sensor_name = device_id
            else:
                sensor_name = sensor_id_mapping[device_id]

            # 3. Notify the world about our nice temperature
            _ = mqtt_client.publish(sensor_name, payload=temp, qos=0, retain=False) 
                
        time.sleep(1)


if __name__ == "__main__":
    try: 
        measurement_loop()
    except KeyboardInterrupt:
        logger.info("##### Shutdown by Keyboard Interrupt#####")
    except Exception as e:
        logger.exception(e)
        raise e
