import paho.mqtt.client as paho
import time

# def on_connect(client, userdata, flags, rc):
#     logger.debug("Connected with result code " + str(rc))
#     if rc == 0:
#         logger.info("Connected to broker")
#     else:
#         logger.info("Connection failed")

def create_mqtt_client(client_id, broker, port, **kwargs):
    # Create the MQTT client
    mqtt_client = paho.Client(client_id)
    # mqtt_client.on_connect = on_connect
    
    # Connect the MQTT client
    mqtt_client.connect(broker, port) # establish connection
    mqtt_client.loop_start()
    while not mqtt_client.is_connected(): # Wait for connection
        time.sleep(0.1)
    
    return mqtt_client