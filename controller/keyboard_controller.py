import os
import sys
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from pynput import keyboard
import argparse
from comms.mqtt import interface as mqtt_interface

def mqtt_callback(client, userdata, message):
    pass

def on_press(key):
    if key == keyboard.Key.esc:
        print("Stopping listener!")
        return False
    try:
        k = key.char
    except:
        k = key.name
    mqtt_manager.send_message(mqtt_id, k)

parser = argparse.ArgumentParser()
parser.add_argument("mqtt_id", type=str, help="MQTT ID")
parser.add_argument("--local", help="Connect to stream over LAN", action="store_true")
args = parser.parse_args()

mqtt_id = args.mqtt_id
mqtt_targets = ["laptop"]
mqtt_topics = []
mqtt_manager = mqtt_interface.MqttInterface(id=mqtt_id, targets=mqtt_targets, topics=mqtt_topics, callback=mqtt_callback, local=True if args.local else False)
runtime_config = 0
mqtt_manager.start_reading()

listener = keyboard.Listener(on_press=on_press)
listener.start()

while True:
    pass