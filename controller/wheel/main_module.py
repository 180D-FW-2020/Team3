import os
import sys
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../..')))

from comms.mqtt import interface as mqtt_interface
from comms.pyserial.serial_threaded import SerialInterface
from comms.proto import motor_requests_pb2
import threading
import time

def mqtt_callback(client, userdata, message):
    # Print all messages
    payload = message.payload
    topic = message.topic
    mqtt_manager.pulse_check(topic, payload.decode("utf-8"))

    '''
    print('Received message: "' + payload +
          '" on topic "' + topic + '" with QoS ' + str(message.qos))
    '''

def generate_motor_request(joy_value):
    proto_request = motor_requests_pb2.MotorRequest()
    lower_zero = 470
    upper_zero = 530

    proto_request.angle = 0 # Update!

    joy_value = int(joy_value)
    if joy_value > lower_zero and joy_value < upper_zero:
        proto_request.throttle = 0
        proto_request.direction = 0
        proto_request.angle = 0
    elif joy_value > upper_zero:
        proto_request.throttle = int(100 * float(joy_value-upper_zero) / (1023-upper_zero))
        proto_request.direction = 2
    elif joy_value < lower_zero:
        proto_request.throttle = int(100 * float(joy_value-lower_zero) / (0-lower_zero))
        proto_request.direction = 1

    return proto_request

mqtt_id = "wheel"
mqtt_targets = ["laptop"]
mqtt_topics = []
mqtt_manager = mqtt_interface.MqttInterface(id=mqtt_id, targets=mqtt_targets, topics=mqtt_topics, callback=mqtt_callback)
mqtt_manager.start_reading()

# First connect to Controller Main
print("Opening connection to Controller Main...")
while not mqtt_manager.handshake("laptop"):
    time.sleep(0.5)

serial_interface = SerialInterface("/dev/tty.usbmodem146301")
thread = threading.Thread(target=serial_interface.read_from_port)
thread.start()

while True:
    if "JOY" in serial_interface.stack:
        motor_request_proto = generate_motor_request(serial_interface.stack.pop("JOY"))
        mqtt_manager.send_message("motor_requests", motor_request_proto.SerializeToString())
