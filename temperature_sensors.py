#!/usr/bin/python3
#Source: https://www.earth.li/~noodles/blog/2018/05/rpi-mqtt-temp.html

import os
import glob
import time
import subprocess
import socket
import logging

# 3rd party libraries
import paho.mqtt.client as paho
import hydra
from omegaconf import DictConfig

# Global variables
Connected = False
logger = logging.getLogger("TemperatureSensors")
logger.setLevel(logging.DEBUG)

def read_temp(device_id):
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

def on_connect(client, userdata, flags, rc):
    logger.debug("Connected with result code " + str(rc))
    if rc == 0:
        logger.info("Connected to broker")
        global Connected
        Connected = True
    else:
        logger.info("Connection failed")

def on_publish(client, userdata, mid):
    logger.debug("Data published %s"%(str(mid)))

@hydra.main(config_path="config.yaml")
def measurement_loop(cfg):
    # Read the config
    machine = cfg.get('machine', socket.gethostname()) # with default value
    broker = cfg.mqtt.broker
    port = cfg.mqtt.port
    sensor_dir = cfg.sensors.sensor_dir
    sensor_id_mapping = cfg.sensors.mapping

    # Create the MQTT client
    mqtt_client = paho.Client("Python")
    mqtt_client.on_connect = on_connect
    mqtt_client.on_publish = on_publish
    mqtt_client.connect(broker, port) # establish connection
    
    # Connect the MQTT client
    mqtt_client.loop_start()
    while Connected != True: #Wait for connection
        time.sleep(0.1)
        
    
    # Run the measurement and publishing loop 
    while True:

        # Show that we are alive
        mqtt_client.publish(os.path.join(machine, "modules/sensors"), payload=1, retain=False)

        # Retrieve a new list of devices every iteration to allow plug and play
        device_ids = [os.path.basename(x) for x in glob.glob(sensor_dir + '28-*')]

        for device_id in device_ids:

            # 1. Read the Temperature
            temp = read_temp(device_id)

            # 2. Handl reading errors
            if temp is not None:
                topic = os.path.join("sensors", device_id)
                _ = mqtt_client.publish(topic, payload=temp, retain=True) 
            else:
                logger.error("Reading %s failed"%(device_id))
                
            # 3. Notify about missing information
            if device_id not in sensor_id_mapping:
                logger.warning(("No mapping found for %s"%(device_id)))

        time.sleep(1)

if __name__ == "__main__":
    try: 
        print("##### Start Measurement #####")
        measurement_loop()
    except KeyboardInterrupt:
        print("##### Shutdown #####")
        pass