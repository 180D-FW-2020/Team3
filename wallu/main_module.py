import os
import sys
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from comms.mqtt import interface as mqtt_interface
from comms.proto import motor_requests_pb2
from comms.pyserial.serial_threaded import SerialInterface
import time
import threading

def write_motor_request(request):
    req = "M"
    if request.direction == 0:
        req += "S"
    elif request.direction == 1:
        req += "F"
    elif request.direction == 2:
        req += "B"
    else:
        print("Critical Error! Could not generate motor request")
        return
    
    if request.angle < 0:
        req += "N"
    else:
        req += "P"

    angle_mag = abs(request.angle)

    if angle_mag == 0:
        req += "00"
    elif angle_mag < 10:
        req += "0" + str(angle_mag)
    else:
        req += str(angle_mag)

    if request.throttle == 100:
        req += "M0"
    elif request.throttle == 0:
        req += "00"
    elif request.throttle < 10:
        req += "0" + str(request.throttle)
    else:
        req += str(request.throttle)

    req += ";"
    
    serial_interface.write_to_port(req)

def mqtt_callback(client, userdata, message):
    # Print all messages
    payload = message.payload
    topic = message.topic
    mqtt_manager.pulse_check(topic, payload.decode("utf-8"))

    parsed_topic = topic.split('/')[-1]
    if parsed_topic == "motor_requests":
        motor_request = motor_requests_pb2.MotorRequest()
        motor_request.ParseFromString(payload)
        write_motor_request(motor_request)

    '''
    print('Received message: "' + str(payload) +
          '" on topic "' + topic + '" with QoS ' + str(message.qos))
    '''

# PySerial setup
serial_interface = SerialInterface("/dev/ttyUSB0")

# MQTT setup
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