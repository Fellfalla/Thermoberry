# standard libraries
import os
import socket
import logging
import time
import json
import datetime

# 3rd party libraries
import hydra

# Local Variables
import utils
import helpers
from iot_entity import IotEntity


# Global variables
module_name = "HeatingControl"
logger = logging.getLogger(module_name)
machine = socket.gethostname()

class HeatingCircuit(IotEntity):
    def __init__(self):
        super().__init__()
        self.topic_states = {} # stores the current topic states

        # Config values
        self.topic_requested_temperature = None
        self.topic_enable = None
        self.topic_outside_temperature = None
        self.topic_supplier_temperature = None
        self.topic_supplier_charging = None
        self.topic_pump = None
        self.activation_rules = None
        self.room_temperature = None
        self.requested_temperature_calculation = None

        # property and private variables
        self._requested_temperature = -1
        self._automatic_mode = False
        self._stop_events = {}

    @property
    def automatic_mode(self):
        return self._automatic_mode

    @automatic_mode.setter
    def automatic_mode(self, value):
        assert isinstance(value, bool)

        if value is True and not self.update_heating_state in self._stop_events:
            logger.info("Enabling automatic mode of %s"%self.id)
            self._stop_events[self.update_heating_state] = \
                helpers.scheduling.run_periodically(5, self.update_heating_state)
        
        if value is False and self.update_heating_state in self._stop_events:
            # Stop the periodic call of the control method
            logger.info("Disabling automatic mode of %s"%self.id)
            self._stop_events[self.update_heating_state].set()
            del self._stop_events[self.update_heating_state]

        self._automatic_mode = value

    @property
    def target_room_temperature(self):
        clock = datetime.datetime.now().time()
        day_start = datetime.datetime.strptime(self.room_temperature.day_start, '%H:%M').time()
        night_start = datetime.datetime.strptime(self.room_temperature.night_start, '%H:%M').time()
        is_day = helpers.datetime.in_between(clock, day_start, night_start)

        if is_day:
            return self.room_temperature.day
        else:
            return self.room_temperature.night

    def _on_message(self, client, userdata, message):
        msg_payload = json.loads(message.payload.decode())
        if message.topic == self.topic_enable:
            self.automatic_mode = msg_payload
        else:
            self.topic_states[message.topic] = msg_payload

    def enable(self, broker, port):
        client_id="%s@%s"%(self.id, machine)
        topics = [
            self.topic_enable,
            self.topic_supplier_temperature,
            self.topic_supplier_charging,
            self.topic_outside_temperature
        ]

        broker = utils.resolve_mqtt_address(broker)
        self.mqtt_client = helpers.mqtt.callback_nonblocking(
            callback=self._on_message, 
            topics=topics, 
            client_id=client_id, 
            hostname=broker, 
            port=port)

        # Enable calculation of the target output temperature
        self._stop_events[self.update_target_output_temperature] = \
            helpers.scheduling.run_periodically(4, self.update_target_output_temperature)


    def disable(self):

        # Disable calculation of the target output temperature
        self._stop_events[self.update_heating_state].set()
        del self._stop_events[self.update_heating_state]

        self.mqtt_client.disconnect()


    def update_heating_state(self):
        """
        Decide if we want to enable the heating pump or disable it
        """
        enable_heating_circuit = True

        try:
            # Turn off if the supply temperature is too low
            if self.topic_states[self.topic_supplier_temperature] < \
                self.target_room_temperature + self.activation_rules.delta_input_over_room_temperature:

                logger.debug("Turn off %s because temperature is too low"%self.id)                
                enable_heating_circuit = False
 
            # Turn off if supplier is almost empty and charging
            elif self.topic_supplier_charging in self.topic_states and \
                self.topic_states[self.topic_supplier_charging] and \
                self.topic_states[self.topic_supplier_temperature] < self.activation_rules.supplier_temperature_while_charging:
               
                logger.debug("Turn off %s because supplier is charging and low"%self.id)                
                enable_heating_circuit = False

            # Turn off heating, if it get too warm outside
            elif self.target_room_temperature - self.topic_states[self.topic_outside_temperature] < self.activation_rules.delta_inside_outside:
                
                logger.debug("Turn off %s because outside is too warm"%self.id)                
                enable_heating_circuit = False

        except KeyError as e:
            logger.exception(e)

        self.mqtt_client.publish(self.topic_pump, json.dumps(enable_heating_circuit), qos=2, retain=True)

    def update_target_output_temperature(self):
        """
        Calculates the desired output temperature based on the target room termperature and environment temperature
        """

        try:
            current_inside_outside_delta = self.target_room_temperature - self.topic_states[self.topic_outside_temperature]
            slope = self.requested_temperature_calculation.slope
            offset = self.requested_temperature_calculation.offset

            if current_inside_outside_delta > 0:
                # Some ease-off function from delta_t to requested temperature
                self._requested_temperature = slope * current_inside_outside_delta ** 0.5 + self.target_room_temperature + offset
            else:
                # Calculation rule for negative delta is not defined
                pass

        except KeyError as e:
            logger.exception(e)
            requested_temperature = self.requested_temperature_calculation.fallback

        # max temperature limit
        self._requested_temperature = min(self._requested_temperature, self.requested_temperature_calculation.max)
        self._requested_temperature = round(self._requested_temperature, 3) # round for the visuals

        self.mqtt_client.publish(self.topic_requested_temperature, json.dumps(self._requested_temperature), qos=0, retain=False)

@hydra.main(config_path="conf/config.yaml")
def heating_circuit_loop(cfg):
    # Prepare logging
    new_log_level = cfg.logging.level
    logger.info("Setting loglevel to %s"%(str(new_log_level)))
    logger.setLevel(new_log_level)

    # Connect to MQTT broker
    logger.info("Connecting to MQTT broker...")
    main_mqtt_client = utils.create_mqtt_client(client_id="%s@%s"%(module_name,machine), clean_session=True, **cfg.mqtt)
    if main_mqtt_client:
        logger.info("Connection to MQTT broker: OK")
    else:
        logger.error("Connection to MQTT broker: FAILED")
        return

    # Create all the mixers
    heating_circuits = []
    for heating_circuit_cfg in cfg.heating_circuits:
        heating_circuit = HeatingCircuit.from_dict(heating_circuit_cfg)
        heating_circuits.append(heating_circuit)
        assert heating_circuit.id

        heating_circuit.enable(**cfg.mqtt)

    heartbeat_topic = machine + "/modules/" + module_name
    main_mqtt_client.publish(heartbeat_topic, payload=json.dumps(True), qos=2 ,retain=True) # Show that we are alive
    
    # TODO: move this before connect, otherwise is has no effect
    main_mqtt_client.will_set(heartbeat_topic, payload=json.dumps(False), qos=2, retain=True)

    while True:
        time.sleep(1)


if __name__ == "__main__":
    try: 
        # TODO: cleanup the introduction logmsgs
        print("##### Start Heating Circuit Module #####")
        heating_circuit_loop()
    except KeyboardInterrupt:
        print("##### Shutdown #####")
    except SystemExit:
        print("##### Shutdown #####")
    except Exception as e:
        logger.exception(e)
        raise e
