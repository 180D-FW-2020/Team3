import os
import sys
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

import cv2
import socket
from comms.mqtt import interface as mqtt_interface
import time
import numpy as np

def mqtt_callback(client, userdata, message):
    global runtime_config
    
    payload = message.payload.decode("utf-8")
    topic = message.topic

    parsed_topic = message.topic.split('/')[-1]
    if parsed_topic == "runtime_config":
        try:
            new_config = int(payload)
            if new_config != runtime_config:
                runtime_config = new_config
                print("Set runtime config to " + str(runtime_config))
        except:
            print("Could not parse runtime config, resetting to standby.")
            runtime_config = 0

mqtt_id = "cannon"
mqtt_targets = ["laptop"]
mqtt_topics = ["motor_requests", "storage_control", "vitals"]
mqtt_manager = mqtt_interface.MqttInterface(id=mqtt_id, targets=mqtt_targets, topics=mqtt_topics, callback=mqtt_callback)
runtime_config = 0
mqtt_manager.start_reading()

#SERVER_INFO = ("wallu.ddns.net", 50000)
SERVER_INFO = ("172.91.77.126", 50000)
#SERVER_INFO = ("192.168.1.206", 50000)
BUFFER_SIZE = 51200

tcp_client = socket.socket(family=socket.AF_INET, type=socket.SOCK_STREAM)
tcp_client.connect(SERVER_INFO)

# First connect to Controller Main
while runtime_config == 0:
    print("Waiting for instructions from main controller...")
    time.sleep(0.5)

while True:
    
    
    jpg_buffer = tcp_client.recv(BUFFER_SIZE)

    image = cv2.imdecode(np.frombuffer(jpg_buffer, dtype='uint8'), -1)
    image = cv2.resize(image, (1920,1080))

    cv2.imshow("WALLU Stream", image)
    if cv2.waitKey(1) & 0xFF == ord('q'):
        break