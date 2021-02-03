import os
import sys
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

import cv2
from comms.mqtt import interface as mqtt_interface
from comms.tcp_stream import interface as tcp_interface
from comms.proto import hud_pb2, cannon_pb2
from stream_utils import add_text_overlays, overlay_text, PromptManager, overlay_prompts
import time
import numpy as np
import argparse
import subprocess

def filter_target_colors(targets, target_color):
    if current_target_color == "All":
        return targets
    else:
        colored_targets = []
        for target in targets:
            if target[0] == target_color:
                colored_targets.append(target)
        return colored_targets

def detect_color(image_frame, color):
    print(color)
    target_list = []
    hsv_frame = cv2.cvtColor(image_frame, cv2.COLOR_BGR2HSV) 
  
    # Set range for red color and  
    # define mask 
    #136 87 111
    red_lower = np.array([136, 87, 90], np.uint8) 
    red_upper = np.array([180, 255, 255], np.uint8) 
    red_mask = cv2.inRange(hsv_frame, red_lower, red_upper) 
  
    # Set range for blue color and 
    # define mask 
    blue_lower = np.array([94, 150, 0], np.uint8) 
    blue_upper = np.array([120, 255, 255], np.uint8) 
    blue_mask = cv2.inRange(hsv_frame, blue_lower, blue_upper) 
      
    # Morphological Transform, Dilation 
    # for each color and bitwise_and operator 
    # between imageFrame and mask determines 
    # to detect only that particular color 
    kernal = np.ones((5, 5), "uint8") 
      
    # For red color 
    red_mask = cv2.dilate(red_mask, kernal) 
    res_red = cv2.bitwise_and(image_frame, image_frame,  
                              mask = red_mask) 
    
      
    # For blue color 
    blue_mask = cv2.dilate(blue_mask, kernal) 
    res_blue = cv2.bitwise_and(image_frame, image_frame, 
                               mask = blue_mask) 
   
    # Creating contour to track red color 
    contours, hierarchy = cv2.findContours(red_mask, 
                                           cv2.RETR_TREE, 
                                           cv2.CHAIN_APPROX_SIMPLE) 
    if color != "blue":
        for pic, contour in enumerate(contours): 
            area = cv2.contourArea(contour) 
            if(area > 300): 
                x, y, w, h = cv2.boundingRect(contour) 
                parameters = [x,y,w,h]
                target_info = ["red", parameters]
                target_list.append(target_info)
                image_frame = cv2.rectangle(image_frame, (x, y), 
                                        (x + w, y + h), 
                                        (0, 0, 255), 2)
    if color != "red":
        contours, hierarchy = cv2.findContours(blue_mask, 
                                            cv2.RETR_TREE, 
                                            cv2.CHAIN_APPROX_SIMPLE) 
        for pic, contour in enumerate(contours): 
            area = cv2.contourArea(contour) 
            if(area > 300): 
                x, y, w, h = cv2.boundingRect(contour)
                parameters = [x,y,w,h]
                target_info = ["blue", parameters]
                target_list.append(target_info)
                image_frame = cv2.rectangle(image_frame, (x, y), 
                                        (x + w, y + h), 
                                        (255, 0, 0), 2)
    return target_list

def mqtt_callback(client, userdata, message):
    global runtime_config
    global hud_data
    global current_target_color

    topic = message.topic
    parsed_topic = message.topic.split('/')[-1]
    payload = message.payload

    if parsed_topic == "hud_data":
        hud_data = hud_pb2.HudPoint()
        hud_data.ParseFromString(payload)
        return

    if parsed_topic == "runtime_config":
        try:
            new_config = int(payload.decode("utf-8"))
            if new_config != runtime_config:
                runtime_config = new_config
                print("Set runtime config to " + str(runtime_config))
        except:
            print("Could not parse runtime config, resetting to standby.")
            runtime_config = 0

    if parsed_topic == "cannon_status":
        cannon_status.ParseFromString(payload)

    if parsed_topic == "cannon_prompts":
        prompt_manager.add_prompt(payload.decode("utf-8"))

    if parsed_topic == "target_color":
        current_target_color = payload.decode("utf-8")
arg_parser = argparse.ArgumentParser()
arg_parser.add_argument("--local", help="connect to the video stream locally", action="store_true")
args = arg_parser.parse_args()

cannon_status = cannon_pb2.CannonStatus()
current_target_color = "All"

mqtt_id = "game_master"
mqtt_targets = ["laptop"]
mqtt_topics = ["storage_control", "hud_data", "cannon_status", "cannon_prompts", "target_color"]
mqtt_manager = mqtt_interface.MqttInterface(id=mqtt_id, targets=mqtt_targets, topics=mqtt_topics, callback=mqtt_callback, local=True if args.local else False)
runtime_config = 0
mqtt_manager.start_reading()

# set up prompt manager
prompt_manager = PromptManager()

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

    prompt_manager.clear_expired_prompts()

    if hud_data:
        add_text_overlays(image, hud_data, cannon_status)
    overlay_prompts(image, prompt_manager.gather_valid_prompts())
        
    detect_color(image, current_target_color)
    cv2.imshow("WALLU Stream", image)
    if cv2.waitKey(1) & 0xFF == ord('q'):
        break
