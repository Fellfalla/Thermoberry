#!/usr/bin/env python3
# standard libraries
from abc import ABC, abstractmethod
import socket
import threading
import atexit
import signal
import logging
import json
import time

# 3rd party libraries
import paho.mqtt.client as paho

# Local Variables
import utils

machine = socket.gethostname()

class Module(ABC):
    """
    Modules are long living containers that signal to MQTT if they are running.
    They can be used as main component of a service.

    Source: https://www.netways.de/blog/2016/07/21/atexit-oder-wie-man-python-dienste-nicht-beenden-sollte/
    """
    def __init__(self, module_name):
        self.module_name = module_name
        self.module_client = paho.Client(client_id="%s@%s"%(self.module_name, machine), clean_session=True, userdata=None, protocol=paho.MQTTv311)
        self.heartbeat_topic = machine + "/modules/" + self.module_name
        self.loop_timeout = 1

    def connect(self, cfg=None):
        # Register cleanup procedures
        signal.signal(signal.SIGTERM, self._sigterm)
        atexit.register(self._atexit)

        # Connect to MQTT broker
        logger = logging.getLogger(self.module_name)
        logger.info("%s connecting to MQTT broker..."%(self.module_name))

        self.module_client.will_set(self.heartbeat_topic, payload=json.dumps(False), qos=2, retain=True)
        self.module_client.on_connect = lambda *args, **kwargs: logger.info("%s connected to MQTT broker."%(self.module_name))
        self.module_client.on_disconnect = lambda *args, **kwargs: logger.info("%s disconnected from MQTT broker."%(self.module_name))

        # Connect the MQTT client
        broker = utils.resolve_mqtt_address(cfg.mqtt.broker)
        self.module_client.connect(broker, cfg.mqtt.port) # establish connection
        self.module_client.loop_start()
        while not self.module_client.is_connected(): # Wait for connection
            time.sleep(0.1)

        # Implementation of template method pattern
        self._connect(cfg)

    def disconnect(self):
        if self.module_client and self.module_client.is_connected():
            self.module_client.publish(self.heartbeat_topic, payload=json.dumps(False), qos=1, retain=True) # Show that we are offline now
            self.module_client.disconnect()

        self._disconnect()

    def loop(self):
        """
        Sends heartbeat to MQTT broker.
        """
        # Run loop
        while True:
            self.module_client.publish(self.heartbeat_topic, payload=json.dumps(True), qos=2, retain=False) # Show that we are alive
            self._loop()
            time.sleep(self.loop_timeout)

    @abstractmethod
    def _connect(self, cfg=None):
        """
        Template method called by 'connect'
        """
        pass

    @abstractmethod
    def _loop(self):
        """
        Template method called by 'loop'
        """
        pass

    @abstractmethod
    def _disconnect(self):
        """
        Template method called by 'disconnect'
        """
        pass

    def _sigterm(self, signum, frame):
        threading.Thread(target=self._cleanup, name='CleanupThread').start()
    
    def _cleanup(self):
        # Complex cleanup
        pass

    def _atexit(self):
        # Simple cleanup
        self.disconnect()

    @classmethod
    def from_dict(cls, cfg):
        instance = cls()
        instance.__dict__.update(cfg)
        return instance

