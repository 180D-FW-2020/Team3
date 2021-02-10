import os
import sys
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

import cv2
from comms.mqtt import interface as mqtt_interface
from comms.tcp_stream import interface as tcp_interface
from comms.proto import hud_pb2
from comms.proto import cannon_pb2
from comms.proto import target_pb2
from stream_utils import add_text_overlays, overlay_text, PromptManager, overlay_prompts
import time
import numpy as np
import argparse
import subprocess

kTimeOffset = time.time()
millis = lambda: int(round((time.time() - kTimeOffset) * 1000))

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

    
    if parsed_topic == "runtime_config":
        payload = payload.decode("utf-8")
        try:
            new_config = int(payload)
            if new_config != runtime_config:
                runtime_config = new_config
                print("Set runtime config to " + str(runtime_config))
        except:
            print("Could not parse runtime config, resetting to standby.")
            runtime_config = 0

    if parsed_topic == keyboard_mqtt_id:
        payload = payload.decode("utf-8")
        if payload == "w":
            # cannon warmup
            if cannon_status.motor_status == "Idle" and cannon_status.cooldown_timer <= 0:
                warmup_command = cannon_pb2.CannonCommand()
                warmup_command.type = 1
                cannon_status.motor_status = "Warming Up"
                cannon_status.warmup_timer = millis()
                cannon_status.warmup_timer_end = millis() + cannon_status.warmup_duration
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
                cannon_status.cooldown_duration = 1000
                cannon_status.motor_status = "Cooling Down"
                cannon_status.cooldown_timer = millis()
                cannon_status.cooldown_timer_end = millis() + cannon_status.cooldown_duration

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
                fire_prompt = "Cannon firing!"
                prompt_manager.add_prompt(fire_prompt)
                mqtt_manager.send_message("cannon_prompts", fire_prompt)

        if payload == "esc":
            # shutdown
            pass
    if parsed_topic == "target_color":
        payload = payload.decode("utf-8")
        current_target_color = payload
        prompt_manager.add_prompt("Target color selection changed to " + current_target_color)

    if parsed_topic == "target_locations":
        current_scene.ParseFromString(payload)
        



arg_parser = argparse.ArgumentParser()
arg_parser.add_argument("--local", help="connect to the video stream locally", action="store_true")
args = arg_parser.parse_args()

mqtt_id = "cannon"
keyboard_mqtt_id = "cannon_control"
mqtt_targets = ["laptop"]
mqtt_topics = [keyboard_mqtt_id, "hud_data", "target_color", "target_locations"]
mqtt_manager = mqtt_interface.MqttInterface(id=mqtt_id, targets=mqtt_targets, topics=mqtt_topics, callback=mqtt_callback, local=True if args.local else False)
runtime_config = 0
mqtt_manager.start_reading()

# set up prompt manager
prompt_manager = PromptManager()

# set up cannon class
cannon_status = cannon_pb2.CannonStatus()
cannon_status.motor_status = "Idle"
cannon_status.shot_count = 0
cannon_status.warmup_timer = -1
cannon_status.warmup_duration = 1000
cannon_status.warmup_timer_end = -1
cannon_status.cooldown_timer = -1
cannon_status.cooldown_duration = 1000
cannon_status.cooldown_timer_end = -1
cannon_status.overheat_timer = -1
cannon_status.overheat_duration = 4000
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
current_scene = target_pb2.Scene()
current_target_color = "red"

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

    prompt_manager.clear_expired_prompts()

    # process cannon state
    if cannon_status.motor_status == "Warming Up":
        cannon_status.warmup_timer = millis()
        if cannon_status.warmup_timer_end - cannon_status.warmup_timer <= 0:
            # Cannon finished warming up
            warm_prompt = "Cannon warmed up!"
            prompt_manager.add_prompt(warm_prompt)
            mqtt_manager.send_message("cannon_prompts", warm_prompt)
            cannon_status.motor_status = "Warmed Up"
            cannon_status.warmup_timer = -1
            cannon_status.warmup_timer_end = -1
            cannon_status.overheat_timer = millis()
            cannon_status.overheat_timer_end = millis() + cannon_status.overheat_duration

    if cannon_status.motor_status == "Warmed Up":
        cannon_status.overheat_timer = millis()
        if cannon_status.overheat_timer_end - cannon_status.overheat_timer <= 0:
            # Cannon overheated!
            print("Cannon overheated!")
            overheat_prompt = "Cannon overheated!"
            prompt_manager.add_prompt(overheat_prompt)
            mqtt_manager.send_message("cannon_prompts", overheat_prompt)
            cannon_status.motor_status = "Overheated! Cooling Down"
            cannon_status.warmup_timer = -1
            cannon_status.warmup_timer_end = -1
            cannon_status.overheat_timer = -1
            cannon_status.overheat_timer_end = -1
            cannon_status.cooldown_duration = 5000
            cannon_status.cooldown_timer = millis()
            cannon_status.cooldown_timer_end = millis() + cannon_status.cooldown_duration
            cooldown_command = cannon_pb2.CannonCommand()
            cooldown_command.type = 2
            mqtt_manager.send_message("cannon_cmd", cooldown_command.SerializeToString())


    if cannon_status.motor_status in ["Overheated! Cooling Down", "Cooling Down"]:
        cannon_status.cooldown_timer = millis()
        if cannon_status.cooldown_timer_end - cannon_status.cooldown_timer <= 0:
            cooldown_prompt = "Cannon is cool and ready!"
            prompt_manager.add_prompt(cooldown_prompt)
            mqtt_manager.send_message("cannon_prompts", cooldown_prompt)
            cannon_status.motor_status = "Idle"
            cannon_status.cooldown_timer = -1
            cannon_status.cooldown_timer_end = -1

    mqtt_manager.send_message("cannon_status", cannon_status.SerializeToString())

    if hud_data:
        add_text_overlays(image, hud_data, cannon_status)

    overlay_prompts(image, prompt_manager.gather_valid_prompts())
    if current_scene:
        for target in current_scene.targets:
            # draw target
            coords_proto = target.coordinates
            coords = []
            for vertex in coords_proto:
                coords.append(vertex.coord)
            cv2.drawContours(image, [np.array(coords).astype(int)], -1, (0, 255, 0), 2)
    cv2.imshow("WALLU Stream", image)
    if cv2.waitKey(1) & 0xFF == ord('q'):
        break
