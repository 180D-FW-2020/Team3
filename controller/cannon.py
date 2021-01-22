import os
import sys
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

import cv2
import socket
from comms.mqtt import interface as mqtt_interface
from comms.tcp_stream import interface as tcp_interface
import time
import numpy as np
from pynput import keyboard

def on_press(key):
    if key == keyboard.Key.esc:
        print("Stopping listener!")
        return False
    try:
        k = key.char
    except:
        k = key.name
    if k in ['w', 'a', 's', 'd']:
        print("Key pressed: " + k)

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
mqtt_manager = mqtt_interface.MqttInterface(id=mqtt_id, targets=mqtt_targets, topics=mqtt_topics, callback=mqtt_callback, local=False)
runtime_config = 0
mqtt_manager.start_reading()


listener = keyboard.Listener(on_press=on_press)
#listener.start()

REMOTE_SERVER_INFO = ("wallu.ddns.net", 50000)
LOCAL_SERVER_INFO = ("192.168.1.206", 50000)

stream_client = tcp_interface.StreamClient(REMOTE_SERVER_INFO)
stream_client.start()

# First connect to Controller Main
while runtime_config == 0:
    print("Waiting for instructions from main controller...")
    time.sleep(0.5)


while True:
    #stream_client.read_frames()
    
    if not stream_client.frame_init:
        continue

    image = cv2.imdecode(stream_client.frame, -1)
    
    try:
        image = cv2.resize(image, (1920,1080))
    except:
        print("rip")
        print(sys.exc_info()[0])
        continue
    

    cv2.imshow("WALLU Stream", image)
    if cv2.waitKey(1) & 0xFF == ord('q'):
        break
