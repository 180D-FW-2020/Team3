import os
import sys
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../..')))

from comms.mqtt import interface as mqtt_interface
from comms.pyserial.serial_threaded import SerialInterface
from comms.proto import motor_requests_pb2
import compute_angle
import threading
import time

def mqtt_callback(client, userdata, message):
    global runtime_config

    payload = message.payload
    topic = message.topic

    parsed_topic = message.topic.split('/')[-1]
    if parsed_topic == "runtime_config":
        try:
            new_config = int(payload.decode("utf-8"))
            if new_config != runtime_config:
                runtime_config = new_config
                print("Set runtime config to " + str(runtime_config))
        except:
            print("Could not parse runtime config, resetting to standby.")
            runtime_config = 0

def generate_motor_request(joy_value, angle_value):
    proto_request = motor_requests_pb2.MotorRequest()
    lower_zero = 470
    upper_zero = 530

    proto_request.angle = angle_value

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
runtime_config = 0
mqtt_manager.start_reading()

# First connect to Controller Main
while runtime_config == 0:
    print("Waiting for instructions from main controller...")
    time.sleep(0.5)

serial_interface = SerialInterface("/dev/ttyUSB0")
serial_thread = threading.Thread(target=serial_interface.read_from_port)
serial_thread.start()

imu_thread = threading.Thread(target=compute_angle.start_compute, args=(serial_interface.stack,))
imu_thread.start()

while True:
    if "JOY" in serial_interface.stack and "steering_angle" in serial_interface.stack:
        motor_request_proto = generate_motor_request(serial_interface.stack.pop("JOY"), serial_interface.stack["steering_angle"])
        mqtt_manager.send_message("motor_requests", motor_request_proto.SerializeToString())
