import paho.mqtt.client as mqtt

TOPIC_PREFIX = "ece180d/team3/wallu/"
MQTT_QOS = 1


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
    def __init__(self, id, targets, topics, callback=0):
        self.id = id
        self.mqtt_client = mqtt.Client()
        self.mqtt_client.on_connect = self.on_connect
        self.mqtt_client.on_disconnect = on_disconnect

        self.targets = targets
        self.topics = topics
        self.subscribed_topics = []
        self.connected_targets = []
        self.pulses = {}

        if callback == 0:
            callback = default_callback
        self.set_callback(callback)

        # Connect to broker
        self.mqtt_client.connect_async('mqtt.eclipse.org')

    def on_connect(self, client, userdata, flags, rc):
        # Connection request callback
        print("Connection returned result: " + str(rc))

        for target in self.targets:
            target_topic = "pulse_" + str(target)
            self.subscribe(target_topic)

        for topic in self.topics:
            self.subscribe(topic)
            

    def subscribe(self, topic):
        full_topic = TOPIC_PREFIX + str(topic)
        self.mqtt_client.subscribe(full_topic, qos=MQTT_QOS)
        self.subscribed_topics.append(topic)

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

    def pulse_check(self, topic, payload):
        pulse_split = topic.split("pulse_")
        if len(pulse_split) == 2:
            # Received pulse
            target = pulse_split[1]
            if payload == "init" and not target in self.pulses:
                self.pulses[target] = "init"

    def handshake(self, target):
        # Send init message
        self.send_message("pulse_" + self.id, "init")

        # Make sure not already connected to target
        if target in self.connected_targets:
            return True

        if target in self.pulses and self.pulses[target] == "init":
            print("Connected to " + str(target))
            self.connected_targets.append(target)

        