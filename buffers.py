#!/usr/bin/python3
# standard libraries
import os
import socket
import logging
import time 
import json

# 3rd party libraries
import hydra

# Local Variables
import utils
import helpers
from iot_entity import IotEntity

# Global variables
logger = logging.getLogger()
machine = socket.gethostname()


class Buffer(IotEntity):
    def __init__(self):
        super().__init__()
        self.inputs = {}
        self.max_temperatures = {}
        self.min_temperatures = {}
        self.temperatures = {}
        self.temperatures_supply = {}
        self.mqtt_client = None
        
    def update_loading_status(self):
        # Rule 1: temperature too high -> stop loading
        is_hot = any([self.temperatures.get(key,val) > val for key, val in self.max_temperatures.items()])
        
        # Rule 2: temperature too low -> start loading
        is_cold = any([self.temperatures.get(key, val) < val for key, val in self.min_temperatures.items()])

        # Rule 3: check if we have some sufficient supplier
        can_load = any([self.temperatures_supply.get(key,0) > min(self.temperatures.values()) + val.loss for key, val in self.inputs.items()])

        # Rule 4: Force loading if supplier is overheading
        # TODO
        supplier_overheating = False
        
        logger.debug("is_hot: %s | is_cold: %s | can_load: %s"%(is_hot, is_cold, can_load))

        if self.mqtt_client and self.mqtt_client.is_connected():
            if supplier_overheating:
                # protect the supplier by taking the hot water
                self.mqtt_client.publish(self.id + "/load", payload=json.dumps(True), retain=True)
            elif is_hot:
                # stop in case of overheating
                self.mqtt_client.publish(self.id + "/load", payload=json.dumps(False), retain=True)
            elif is_cold and can_load:
                # start loading as soon as we are getting too cold
                self.mqtt_client.publish(self.id + "/load", payload=json.dumps(True), retain=True)
            elif not can_load:
                # disable as soon as we cannot load anymore
                self.mqtt_client.publish(self.id + "/load", payload=json.dumps(False), retain=True)

    def on_temperature_change(self, client, userdata, message):
        self.temperatures[message.topic] = float(message.payload)
        self.update_loading_status()

    def on_input_temperature_change(self, client, userdata, message):
        self.temperatures_supply[message.topic] = float(message.payload)

    def enable(self, broker="localhost", port=1883):
        # Connect to MQTT broker
        logger.info("Connecting %s to MQTT broker."%(self.id))

        client_id="%s@%s"%(self.id, machine)
        topics = []
        topics.extend([topic for topic in self.min_temperatures.keys()])
        topics.extend([topic for topic in self.max_temperatures.keys()])
        logger.debug("Subscribing to %s"%topics)
        self.mqtt_client = helpers.mqtt.callback_nonblocking(
            callback=self.on_temperature_change, 
            topics=topics, 
            client_id=client_id, 
            hostname=broker, 
            port=port)


        topics = [k for k in self.inputs.keys()]
        logger.debug("Subscribing to %s"%topics)
        self.input_client = helpers.mqtt.callback_nonblocking(
            callback=self.on_input_temperature_change, 
            topics=topics, 
            client_id=client_id, 
            hostname=broker, 
            port=port)

    def disable(self):
        if self.mqtt_client and self.mqtt_client.is_connected():
            logger.info("Disconnecting %s from MQTT broker."%(self.id))
            self.mqtt_client.disconnect()

@hydra.main(config_path="conf/config.yaml")
def buffers_loop(cfg):
    # Prepare logging
    global logger
    logger = logging.getLogger("Buffer")
    new_log_level = cfg.logging.level
    logger.info("Setting loglevel to %s"%(str(new_log_level)))
    logger.setLevel(new_log_level)

    # Read the config
    buffers = []
    for buffer in cfg.buffers:
        buffer = Buffer.from_dict(buffer)
        buffers.append(buffer)
        assert buffer.id

        buffer.enable(**cfg.mqtt)

    # Connect to MQTT broker
    logger.info("Connecting to MQTT broker...")
    mqtt_client = utils.create_mqtt_client(client_id="TemperatureModule@%s"%(machine), **cfg.mqtt)
    if mqtt_client:
        logger.info("Connection to MQTT broker: OK")
    else:
        logger.error("Connection to MQTT broker: FAILED")
        return

    heartbeat_topic = machine + "/modules/buffers"
    mqtt_client.publish(heartbeat_topic, payload=json.dumps(True), qos=2 ,retain=True) # Show that we are alive
    mqtt_client.will_set(heartbeat_topic, payload=json.dumps(False), qos=2, retain=True)
    # TODO: add atexit and disconnect the mqtt client then. Looks as if otherwise the "will" will not be sent
    while True:
        time.sleep(1)


if __name__ == "__main__":
    try: 
        print("##### Start Measurement #####")
        buffers_loop()
    except KeyboardInterrupt:
        print("##### Shutdown #####")
        pass