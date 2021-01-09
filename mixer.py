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
module_name = "Mixer"
logger = logging.getLogger(module_name)
machine = socket.gethostname()

class Mixer(IotEntity):
    def __init__(self):
        super().__init__()
        self.output_previous = None
        self.output_actual = None
        self.output_target = None

        # Config values
        self.cycle_period = None
        self.topic_output_actual = None
        self.topic_output_target = None
        self.topic_open = None
        self.topic_close = None
        self.topic_enable = None
        self.temperature_to_time = None
        self.hysteresis = None

        # Parameters of the PID controller
        self.P = 1 # proportion part
        self.I = 0 # integral part
        self.D = 2.8 # differential part

        # property and private variables
        self._automatic_mode = False
        self._stopper = None

    @property
    def automatic_mode(self):
        return self._automatic_mode

    @automatic_mode.setter
    def automatic_mode(self, value):
        assert isinstance(value, bool)

        if value is True and self._stopper is None:
            logger.info("Enabling automatic mode of %s"%self.id)
            self._stopper = helpers.scheduling.run_periodically(self.cycle_period, self.control)
        
        if value is False and self._stopper is not None:
            # Stop the periodic call of the control method
            logger.info("Disabling automatic mode of %s"%self.id)
            self._stopper.set()
            self._stopper = None

        self._automatic_mode = value

    def _on_message(self, client, userdata, message):
        if message.topic == self.topic_output_actual:
            self.output_actual = float(message.payload)
            if self.output_previous is None:
                self.output_previous = self.output_actual

        elif message.topic == self.topic_output_target:
            self.output_target = float(message.payload)

        elif message.topic == self.topic_enable:
            self.automatic_mode = json.loads(message.payload.decode())

        else:
            logger.warn("Unexpected topic %s"%message.topic)

    def enable(self, broker, port):
        client_id="%s@%s"%(self.id, machine)
        topics = [
            self.topic_output_actual,
            self.topic_output_target,
            self.topic_enable
        ]

        self.mqtt_client = helpers.mqtt.callback_nonblocking(
            callback=self._on_message, 
            topics=topics, 
            client_id=client_id, 
            hostname=broker, 
            port=port)

    def disable(self):
        self.mqtt_client.disconnect()

    def control(self):
        """
        Calling this method will start a periodic loop
        
        The feedback controller is based on a simple PD controller
        """
        if self.output_target is None:
            logger.warn("No target temperature set")
            return
        if self.output_actual is None:
            logger.warn("Unknown output temperature")
            return

        # Calculate the targeted temperature change for this period
        tendency = self.output_actual - self.output_previous
        error_temp = self.output_target - self.output_actual
        delta = (self.P * error_temp - self.D * tendency)
        self.output_previous = self.output_actual

        if abs(delta) > self.hysteresis:
            
            # Topic depends on if we need to open or close the mixer
            topic = self.topic_open if delta > 0 else self.topic_close

            # Calc the duty cycle
            duty_time = min(max(self.temperature_to_time * abs(delta), 0), self.cycle_period)
            
            # Send commands via MQTT
            self.mqtt_client.publish(topic, payload=json.dumps(True), qos=2)
            time.sleep(duty_time)
            self.mqtt_client.publish(topic, payload=json.dumps(False), qos=2)



@hydra.main(config_path="conf/config.yaml")
def mixer_loop(cfg):
    # Prepare logging
    new_log_level = cfg.logging.level
    logger.info("Setting loglevel to %s"%(str(new_log_level)))
    logger.setLevel(new_log_level)

    # Connect to MQTT broker
    logger.info("Connecting to MQTT broker...")
    mqtt_client = utils.create_mqtt_client(client_id="%s@%s"%(module_name, machine), **cfg.mqtt)
    if mqtt_client:
        logger.info("Connection to MQTT broker: OK")
    else:
        logger.error("Connection to MQTT broker: FAILED")
        return

    # Create all the mixers
    mixers = []
    for mixer_cfg in cfg.mixers:
        mixer = Mixer.from_dict(mixer_cfg)
        mixers.append(mixer)
        assert mixer.id

        mixer.enable(**cfg.mqtt)

    heartbeat_topic = machine + "/modules/" + module_name
    mqtt_client.publish(heartbeat_topic, payload=json.dumps(True), qos=2 ,retain=True) # Show that we are alive
    mqtt_client.will_set(heartbeat_topic, payload=json.dumps(False), qos=2, retain=True)

    while True:
        time.sleep(1)
    # mqtt_client.loop_forever()

if __name__ == "__main__":
    try: 
        print("##### Start Measurement #####")
        mixer_loop()
    except KeyboardInterrupt:
        print("##### Shutdown #####")
        pass
    except Exception as e:
        logger.exception(e)
        raise e
