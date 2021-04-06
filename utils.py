import paho.mqtt.client as paho
import time
import socket

# def on_connect(client, userdata, flags, rc):
#     logger.debug("Connected with result code " + str(rc))
#     if rc == 0:
#         logger.info("Connected to broker")
#     else:
#         logger.info("Connection failed")

def resolve_mqtt_address(hostname):
    return str(socket.gethostbyname(socket.getfqdn(hostname)))

# TODO: Consider creating a wrapper class
def create_mqtt_client(client_id, broker, port, clean_session=None, **kwargs):
    # Create the MQTT client
    # TODO Try out clean_session=True
    mqtt_client = paho.Client(client_id, clean_session=clean_session)
    # mqtt_client.on_connect = on_connect
    
    # Connect the MQTT client
    broker = resolve_mqtt_address(broker)
    mqtt_client.connect(broker, port) # establish connection
    mqtt_client.loop_start()
    while not mqtt_client.is_connected(): # Wait for connection
        time.sleep(0.1)
    
    return mqtt_client