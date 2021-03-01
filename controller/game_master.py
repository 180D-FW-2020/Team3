import os
import sys
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

import cv2
from comms.mqtt import interface as mqtt_interface
from comms.tcp_stream import interface as tcp_interface
from comms.proto import hud_pb2, cannon_pb2, target_pb2
from stream_utils import add_text_overlays, overlay_text, PromptManager, overlay_prompts, overlay_image
import time
import numpy as np
import argparse
import subprocess
from contour_recognition import target_recognition_2

global hue
global saturation
global valu

global thresholds = [0, 0, 0, 0, 0, 0]

def on_mouse(event, x, y, flags, param):
    if event == cv2.EVENT_LBUTTONDOWN:
        if x > exit_icon_coords[0][0] and x < exit_icon_coords[0][1] and y > exit_icon_coords[1][0] and y < exit_icon_coords[1][1]:
            print("Exit click detected!")
            cv2.destroyAllWindows()
            process.kill()
            sys.exit()

def filter_target_colors(targets, target_color):
    if current_target_color == "All":
        return targets
    else:
        colored_targets = []
        for target in targets:
            if target[0] == target_color:
                colored_targets.append(target)
        return colored_targets

def mqtt_callback(client, userdata, message):
    global runtime_config
    global hud_data
    global current_target_color

    global thresholds

    topic = message.topic
    parsed_topic = message.topic.split('/')[-1]
    payload = message.payload

    if parsed_topic == "hud_data":
        hud_data = hud_pb2.HudPoint()
        hud_data.ParseFromString(payload)
        return

    if parsed_topic == "upper_thresh":
        payload = payload.decode('utf-8')
        new_values = payload.split()
        hue = int(new_values[0], 16)
        sat = int(new_values[1], 16)
        val = int(new_values[2], 16)
        l_hue = int(new_values[3], 16)
        l_sat = int(new_values[4], 16)
        l_val = int(new_values[5], 16)
        thresholds[0] = hue
        thresholds[1] = sat
        thresholds[2] = val
        thresholds[3] = l_hue
        thresholds[4] = l_sat
        thresholds[5] = l_val


    if parsed_topic == "runtime_config":
        try:
            new_config = int(payload.decode("utf-8"))
            if new_config != runtime_config:
                runtime_config = new_config
                print("Set runtime config to " + str(runtime_config))
                if runtime_config == 0:
                    stream_client.connected = False
        except:
            print("Could not parse runtime config, resetting to standby.")
            runtime_config = 0

    if parsed_topic == "cannon_status":
        cannon_status.ParseFromString(payload)

    if parsed_topic == "cannon_prompts":
        prompt_manager.add_prompt(payload.decode("utf-8"))

    if parsed_topic == "target_color":
        current_target_color = payload.decode("utf-8")
        prompt_manager.add_prompt("Target color selection changed to " + current_target_color)

arg_parser = argparse.ArgumentParser()
arg_parser.add_argument("--local", help="connect to the video stream locally", action="store_true")
arg_parser.add_argument("--mic_index", help="choose a custom mic index (default 0)")
args = arg_parser.parse_args()

cannon_status = cannon_pb2.CannonStatus()
current_target_color = "red"

mqtt_id = "game_master"
voice_mqtt_id = "voice_control"
mqtt_targets = ["laptop"]
mqtt_topics = ["upper_thresh", "storage_control", "hud_data", "cannon_status", "cannon_prompts", "target_color"]
mqtt_manager = mqtt_interface.MqttInterface(id=mqtt_id, targets=mqtt_targets, topics=mqtt_topics, callback=mqtt_callback, local=True if args.local else False)
runtime_config = 0
mqtt_manager.start_reading()

# set up prompt manager
prompt_manager = PromptManager()


# Launch voice script
if args.mic_index:
    mic_index = str(args.mic_index)
else:
    mic_index = "0"
voice_subprocess = ["python3", "voice_unlock.py", voice_mqtt_id, "--mic_index="+mic_index]
if args.local:
    voice_subprocess.append("--local")
process = subprocess.Popen(voice_subprocess)


REMOTE_SERVER_INFO = ("wallu.ddns.net", 50000)
LOCAL_SERVER_INFO = ("192.168.1.206", 50000)
CHOSEN_SERVER_INFO = LOCAL_SERVER_INFO if args.local else REMOTE_SERVER_INFO

stream_client = tcp_interface.StreamClient(CHOSEN_SERVER_INFO)
stream_client.start()

load_screen = cv2.imread("graphics/loadscreen.png", -1)
load_screen = cv2.resize(load_screen, (1920,1080), interpolation=cv2.INTER_AREA)
exit_icon = cv2.imread("graphics/icons/logout.png", -1)
exit_icon = cv2.resize(exit_icon, (40, 40), interpolation=cv2.INTER_AREA)
exit_icon_coords = []

hud_data = None

while True:
    if runtime_config == 0:
        image = load_screen
        overlay_image(image, exit_icon, [image.shape[1]-80, 50])
        exit_icon_coords = [ [image.shape[1]-80, image.shape[1]-40], [50, 90] ]
        cv2.imshow("WALLU Stream: Game Master", image)
        cv2.setMouseCallback("WALLU Stream: Game Master", on_mouse)
        if cv2.waitKey(1) & 0xFF == ord('q'):
            break
        time.sleep(0.5)
        continue

    if not stream_client.frame_init:
        continue

    image = cv2.imdecode(stream_client.frame, -1)
    try:
        image = cv2.resize(image, (1920,1080))
    except:
        print("rip")
        print(sys.exc_info()[0])
        continue

    overlay_image(image, exit_icon, [image.shape[1]-80, 50])
    exit_icon_coords = [ [image.shape[1]-80, image.shape[1]-40], [50, 90] ]
    prompt_manager.clear_expired_prompts()

    if hud_data:
        add_text_overlays(image, hud_data, cannon_status)
    overlay_prompts(image, prompt_manager.gather_valid_prompts())
        
    #detect_color(image, current_target_color)
    targets = target_recognition_2(image, current_target_color, thresholds)
    targets_proto = target_pb2.Scene()
    for target in targets:
        target_proto = target_pb2.Target()
        target_proto.color = target[0]
        for coord in target[1]:
            coord_proto = target_pb2.Coord()
            for num in coord:
                coord_proto.coord.append(num)
            target_proto.coordinates.append(coord_proto)
        targets_proto.targets.append(target_proto)
    mqtt_manager.send_message("target_locations", targets_proto.SerializeToString())
    for target in targets:
        cv2.drawContours(image, [target[1].astype(int)], -1, (0, 255, 0), 2)
    
    cv2.setMouseCallback("WALLU Stream: Game Master", on_mouse)
    cv2.imshow("WALLU Stream: Game Master", image)
    if cv2.waitKey(1) & 0xFF == ord('q'):
        break
