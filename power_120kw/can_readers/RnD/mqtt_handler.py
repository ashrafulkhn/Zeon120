from datasets import Datasets, DataHandler
import paho.mqtt.client as mqtt

# Setter function to update demand data
def set_demand(data):
    global demand_data
    demand_data = data
    print(f"Demand updated to: {demand_data}")

# Callback when the client connects to the broker
def on_connect(client, userdata, flags, rc):
    print("Connected with result code " + str(rc))
    client.subscribe("demand")

# Callback when a message is received
def on_message(client, userdata, msg):
    payload = msg.payload.decode()
    print(f"Message received on topic {msg.topic}: {payload}")
    # set_demand(payload)
    DataHandler.updateMessage(payload)

def connect_mqtt(broker_host='test.mosquitto.org', broker_port=1883, keepalive=60):
    client = mqtt.Client()
    client.on_connect = on_connect
    client.on_message = on_message
    client.connect(broker_host, broker_port, keepalive)
    print("Mqtt connected.")
    return client

def setupMqtt():
    # MQTT client setup
    # client = mqtt.Client()
    client = connect_mqtt()  # connects to test.mosquitto.org

    # Connect to the MQTT broker (adjust host and port as needed)
    # client.connect("localhost", 1883, 60)

    client.loop_start()