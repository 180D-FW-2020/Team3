'''
To start broker, run:
/usr/local/sbin/mosquitto -c comms/mqtt/config/mosquitto.conf
'''

import paho.mqtt.client as mqtt
import threading
import time

TOPIC_PREFIX = "ece180d/team3/wallu/"
MQTT_QOS = 1
PULSE_PERIOD = 250

millis = lambda: int(round(time.time() * 1000))

def on_disconnect(client, userdata, rc):
    # Disconnect callback
    if rc != 0:
        print("Unexpected disconnect")
    else:
        print("Expected disconnect")


def default_callback(client, userdata, message):
    # Default callback
    print('Received message: "' + str(message.payload) +
          '" on topic "' + message.topic + '" with QoS ' + str(message.qos))


class MqttInterface:
    def __init__(self, id, targets, topics, callback=0, alpha=False):
        self.id = id
        self.mqtt_client = mqtt.Client()
        self.mqtt_client.on_connect = self.on_connect
        self.mqtt_client.on_disconnect = on_disconnect
        self.targets = targets
        self.alpha = alpha
        self.last_pulse = 0

        self.topics = topics
        self.pulses = {}

        if callback == 0:
            callback = default_callback
        self.set_callback(callback)

        # Connect to broker
        self.mqtt_client.connect_async('192.168.1.206')

    def on_connect(self, client, userdata, flags, rc):
        # Connection request callback
        if rc != 0:
            print("Could not establish connection to MQTT server. Returned code " + str(rc))

        print("Connected to MQTT broker.")

        for topic in self.topics:
            self.subscribe(topic)

        if self.alpha:
            self.subscribe("pulse")
        else:
            self.subscribe("runtime_config")
            pulse_thread = threading.Thread(target=self.pulse_forever)
            pulse_thread.start()

    def subscribe(self, topic):
        full_topic = TOPIC_PREFIX + str(topic)
        self.mqtt_client.subscribe(full_topic, qos=MQTT_QOS)

    def set_callback(self, callback):
        self.mqtt_client.on_message = callback

    def send_message(self, topic, message):
        full_topic = TOPIC_PREFIX + str(topic)
        self.mqtt_client.publish(full_topic, message, qos=MQTT_QOS)

    def start_reading(self):
        self.mqtt_client.loop_start()

    def close_connection(self):
        self.mqtt_client.loop_stop()
        self.mqtt_client.disconnect()

    def register_pulse(self, target):
        if target in self.targets:
            self.pulses[target] = millis()
            print("Registered pulse from: " + target)
        else:
            print("Received pulse from unrecognized target: " + target)

    def target_check(self, target):
        return (target in self.pulses) and (millis() - self.pulses[target] < 1.5*PULSE_PERIOD)

    def pulse_forever(self):
        # Send init message
        while True:
            time_elapsed = millis() - self.last_pulse
            if  time_elapsed >= PULSE_PERIOD:
                self.send_message("pulse", self.id)
                self.last_pulse = millis()
