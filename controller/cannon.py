import os
import sys
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

import cv2
import socket
from comms.mqtt import interface as mqtt_interface
from comms.tcp_stream import interface as tcp_interface
from comms.proto import hud_pb2
from comms.proto import cannon_pb2
from stream_utils import add_text_overlays, overlay_text
import time
import numpy as np
import argparse
import subprocess

def mqtt_callback(client, userdata, message):
    global runtime_config
    global hud_data

    topic = message.topic
    parsed_topic = message.topic.split('/')[-1]
    payload = message.payload

    if parsed_topic == "hud_data":
        hud_data = hud_pb2.HudPoint()
        hud_data.ParseFromString(payload)
        return

    payload = payload.decode("utf-8")
    if parsed_topic == "runtime_config":
        try:
            new_config = int(payload)
            if new_config != runtime_config:
                runtime_config = new_config
                print("Set runtime config to " + str(runtime_config))
        except:
            print("Could not parse runtime config, resetting to standby.")
            runtime_config = 0

    if parsed_topic == keyboard_mqtt_id:
        if payload == "w":
            # cannon warmup
            if cannon_status.motor_status == "Idle" and cannon_status.cooldown_timer <= 0:
                warmup_command = cannon_pb2.CannonCommand()
                warmup_command.type = 1
                cannon_status.motor_status = "Warming Up"
                cannon_status.warmup_timer = int(time.time())
                cannon_status.warmup_timer_end = int(time.time()) + cannon_status.warmup_duration
                mqtt_manager.send_message("cannon_cmd", warmup_command.SerializeToString())

        if payload == "s":
            # cannon cooldown
            if not cannon_status in ["Idle", "Cooling Down", "Overheated! Cooling Down"]:
                cooldown_command = cannon_pb2.CannonCommand()
                cooldown_command.type = 2
                cannon_status.warmup_timer = -1
                cannon_status.warmup_timer_end = -1
                cannon_status.overheat_timer = -1
                cannon_status.overheat_timer_end = -1
                cannon_status.cooldown_duration = 1
                cannon_status.motor_status = "Cooling Down"
                cannon_status.cooldown_timer = int(time.time())
                cannon_status.cooldown_timer_end = int(time.time()) + cannon_status.cooldown_duration

                mqtt_manager.send_message("cannon_cmd", cooldown_command.SerializeToString())

        if payload == "space":
            # cannon fire
            print("Detected space")
            if cannon_status.motor_status == "Warmed Up":
                fire_command = cannon_pb2.CannonCommand()
                fire_command.type = 3
                cannon_status.shot_count += 1
                mqtt_manager.send_message("cannon_cmd", fire_command.SerializeToString())
                print("Sending fire command!")

        if payload == "esc":
            # shutdown
            pass



arg_parser = argparse.ArgumentParser()
arg_parser.add_argument("--local", help="connect to the video stream locally", action="store_true")
args = arg_parser.parse_args()

mqtt_id = "cannon"
keyboard_mqtt_id = "cannon_control"
mqtt_targets = ["laptop"]
mqtt_topics = ["motor_requests", "storage_control", "vitals", keyboard_mqtt_id, "hud_data"]
mqtt_manager = mqtt_interface.MqttInterface(id=mqtt_id, targets=mqtt_targets, topics=mqtt_topics, callback=mqtt_callback, local=True if args.local else False)
runtime_config = 0
mqtt_manager.start_reading()

# set up cannon class
cannon_status = cannon_pb2.CannonStatus()
cannon_status.motor_status = "Idle"
cannon_status.shot_count = 0
cannon_status.warmup_timer = -1
cannon_status.warmup_duration = 1
cannon_status.warmup_timer_end = -1
cannon_status.cooldown_timer = -1
cannon_status.cooldown_duration = 1
cannon_status.cooldown_timer_end = -1
cannon_status.overheat_timer = -1
cannon_status.overheat_duration = 5
cannon_status.overheat_timer_end = -1

cannon_subprocess = ["python3", "keyboard_controller.py", keyboard_mqtt_id]
if args.local:
    cannon_subprocess.append("--local")
process = subprocess.Popen(cannon_subprocess)

REMOTE_SERVER_INFO = ("wallu.ddns.net", 50000)
LOCAL_SERVER_INFO = ("192.168.1.206", 50000)
CHOSEN_SERVER_INFO = LOCAL_SERVER_INFO if args.local else REMOTE_SERVER_INFO

stream_client = tcp_interface.StreamClient(CHOSEN_SERVER_INFO)
stream_client.start()

# First connect to Controller Main
while runtime_config == 0:
    print("Waiting for instructions from main controller...")
    time.sleep(0.5)

hud_data = None

while True:
    
    if not stream_client.frame_init:
        continue

    image = cv2.imdecode(stream_client.frame, -1)
    
    try:
        image = cv2.resize(image, (1920,1080))
    except:
        print("rip")
        print(sys.exc_info()[0])
        continue

    # process cannon state
    if cannon_status.motor_status == "Warming Up":
        cannon_status.warmup_timer = int(time.time())
        if cannon_status.warmup_timer_end - cannon_status.warmup_timer <= 0:
            # Cannon finished warming up
            print("Cannon warmed up!")
            cannon_status.motor_status = "Warmed Up"
            cannon_status.warmup_timer = -1
            cannon_status.warmup_timer_end = -1
            cannon_status.overheat_timer = int(time.time())
            cannon_status.overheat_timer_end = int(time.time()) + cannon_status.overheat_duration

    if cannon_status.motor_status == "Warmed Up":
        cannon_status.overheat_timer = int(time.time())
        if cannon_status.overheat_timer_end - cannon_status.overheat_timer <= 0:
            # Cannon overheated!
            print("Cannon overheated!")
            cannon_status.motor_status = "Overheated! Cooling Down"
            cannon_status.warmup_timer = -1
            cannon_status.warmup_timer_end = -1
            cannon_status.overheat_timer = -1
            cannon_status.overheat_timer_end = -1
            cannon_status.cooldown_duration = 5
            cannon_status.cooldown_timer = int(time.time())
            cannon_status.cooldown_timer_end = int(time.time()) + cannon_status.cooldown_duration
            cooldown_command = cannon_pb2.CannonCommand()
            cooldown_command.type = 2
            mqtt_manager.send_message("cannon_cmd", cooldown_command.SerializeToString())


    if cannon_status.motor_status in ["Overheated! Cooling Down", "Cooling Down"]:
        cannon_status.cooldown_timer = int(time.time())
        if cannon_status.cooldown_timer_end - cannon_status.cooldown_timer <= 0:
            cannon_status.motor_status = "Idle"
            cannon_status.cooldown_timer = -1
            cannon_status.cooldown_timer_end = -1

    mqtt_manager.send_message("cannon_status", cannon_status.SerializeToString())

    if hud_data:
        add_text_overlays(image, hud_data)

    cv2.imshow("WALLU Stream", image)
    if cv2.waitKey(1) & 0xFF == ord('q'):
        break
