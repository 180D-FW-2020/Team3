import os
import sys
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from comms.mqtt import interface as mqtt_interface
from comms.proto import motor_requests_pb2
import time

def mqtt_callback(client, userdata, message):
    # Print all messages
    payload = message.payload
    topic = message.topic
    mqtt_manager.pulse_check(topic, payload.decode("utf-8"))

    parsed_topic = topic.split('/')[-1]
    if parsed_topic == "motor_requests":
        motor_request = motor_requests_pb2.MotorRequest()
        motor_request.ParseFromString(payload)
        print(str(motor_request.throttle) + " " + str(motor_request.direction))

    '''
    print('Received message: "' + str(payload) +
          '" on topic "' + topic + '" with QoS ' + str(message.qos))
    '''



mqtt_id = "wallu"
mqtt_targets = ["laptop"]
mqtt_topics = ["motor_requests"]
mqtt_manager = mqtt_interface.MqttInterface(id=mqtt_id, targets=mqtt_targets, topics=mqtt_topics, callback=mqtt_callback)
mqtt_manager.start_reading()

print("Opening connection to Controller Main...")
while not mqtt_manager.handshake("laptop"):
    time.sleep(0.5)

while True:
    pass