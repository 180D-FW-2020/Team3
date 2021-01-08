import os
import sys
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from comms.mqtt import interface as mqtt_interface
from comms.proto import motor_requests_pb2
from comms.proto import vitals_pb2
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
    decoded_payload = ""
    try:
        decoded_payload = payload.decode("utf-8")
    except:
        pass

    parsed_topic = topic.split('/')[-1]

    if parsed_topic == "runtime_config":
        try:
            runtime_config = int(decoded_payload)
            print("Set runtime config to " + str(runtime_config))
        except:
            print("Could not parse runtime config, resetting to standby.")
            runtime_config = 0

    if parsed_topic == "motor_requests":
        motor_request = motor_requests_pb2.MotorRequest()
        motor_request.ParseFromString(payload)
        write_motor_request(motor_request)

    if parsed_topic == "storage_control":
        if decoded_payload == "unlock0":
            print("Initiating unlock sequence...")
            serial_interface.write_to_port("u0;")
        elif decoded_payload == "unlock1":
            print("Unlocking compartment...")
            serial_interface.write_to_port("u1;")
        elif decoded_payload == "unlock2":
            print("Unlock aborted...")
            serial_interface.write_to_port("u2;")

    '''
    print('Received message: "' + str(payload) +
          '" on topic "' + topic + '" with QoS ' + str(message.qos))
    '''

def generate_vitals_message(last_message):
    proto_msg = vitals_pb2.Vitals()

    parsed = last_message.split("-")
    
    proto_msg.battery_voltage = int(parsed[0])
    proto_msg.payload = parsed[1]
    return proto_msg

# PySerial setup
serial_interface = SerialInterface("/dev/ttyUSB0")
serial_thread = threading.Thread(target=serial_interface.read_from_port)
serial_thread.start()

# MQTT setup
mqtt_id = "wallu"
mqtt_targets = ["laptop"]
mqtt_topics = ["motor_requests", "storage_control"]
mqtt_manager = mqtt_interface.MqttInterface(id=mqtt_id, targets=mqtt_targets, topics=mqtt_topics, callback=mqtt_callback)
mqtt_manager.start_reading()
runtime_config = 0

# First connect to Controller Main
while runtime_config == 0:
    print("Waiting for instructions from main controller...")
    time.sleep(0.5)

while True:
    if "VIT" in serial_interface.stack:
        vitals_proto = generate_vitals_message(serial_interface.stack.pop("VIT"))
        print("Sending vitals!")
        mqtt_manager.send_message("vitals", vitals_proto.SerializeToString())
