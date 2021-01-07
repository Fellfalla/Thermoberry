#!/usr/bin/python3
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
logger = logging.getLogger("TemperatureSensors")

def read_temp(sensor_dir, device_id):
    valid = False
    temp = 0

    measurement_path = os.path.join(sensor_dir, device_id, 'w1_slave')
    with open(measurement_path , 'r') as f:
        for line in f:
            if line.strip()[-3:] == 'YES':
                valid = True
            temp_pos = line.find(' t=')
            if temp_pos != -1:
                temp = float(line[temp_pos + 3:]) / 1000.0

    if valid:
        return temp
    else:
        return None

@hydra.main(config_path="conf/config.yaml")
def measurement_loop(cfg):
    # Read the config
    machine = cfg.get('machine', socket.gethostname()) # with default value
    sensor_dir = cfg.sensors.sensor_dir
    sensor_id_mapping = cfg.sensors.mapping
    qos = cfg.sensors.quality_of_service

    # Prepare logging
    new_log_level = cfg.logging.level
    logger.info("Setting loglevel to %s"%(str(new_log_level)))
    logger.setLevel(new_log_level)

    # Connect to MQTT broker
    logger.info("Connecting to MQTT broker...")
    mqtt_client = utils.create_mqtt_client(client_id="TemperatureModule@%s"%(machine), **cfg.mqtt)
    if mqtt_client:
        logger.info("Connection to MQTT broker: OK")
    else:
        logger.error("Connection to MQTT broker: FAILED")
        return

    # Run the measurement and publishing loop 
    logger.info("Run measurement loop")

    heartbeat_topic = machine + "/modules/sensors"
    mqtt_client.publish(heartbeat_topic, payload=json.dumps(True), qos=2, retain=True) # Show that we are alive
    mqtt_client.will_set(heartbeat_topic, payload=json.dumps(False), qos=2, retain=True)

    while True:

        # Retrieve a new list of devices every iteration to allow plug and play
        device_ids = [os.path.basename(x) for x in glob.glob(os.path.join(sensor_dir, '28-*'))]
        

        for device_id in device_ids:

            # 1. Read the Temperature
            logger.debug("Reading device %s"%(device_id))
            temp = read_temp(sensor_dir, device_id)
                
            # 2. Notify about missing information
            if device_id not in sensor_id_mapping:
                logger.warning(("No mapping found for %s"%(device_id)))
                sensor_name = device_id
            else:
                sensor_name = sensor_id_mapping[device_id]

            # 3. Handl reading errors
            if temp is not None:
                _ = mqtt_client.publish(sensor_name + "/temperature", payload=temp, qos=qos, retain=True) 
                _ = mqtt_client.publish(sensor_name + "/id", payload=device_id, qos=qos, retain=True) 
                
            else:
                logger.error("Reading %s failed"%(device_id))

        time.sleep(1)


if __name__ == "__main__":
    try: 
        measurement_loop()
    except KeyboardInterrupt:
        logger.info("##### Shutdown by Keyboard Interrupt#####")
    except Exception as e:
        logger.exception(e)