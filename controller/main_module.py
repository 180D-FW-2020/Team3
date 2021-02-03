import os
import sys
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

import cv2
import imagezmq
import contour_recognition
#import voice_unlock
from comms.mqtt import interface as mqtt_interface
from comms.tcp_stream import interface as tcp_interface
from comms.proto import hud_pb2, cannon_pb2, vitals_pb2, motor_requests_pb2
from stream_utils import add_text_overlays, overlay_text, overlay_prompts, PromptManager
import time
import threading
import pose_detect
import numpy as np
import subprocess
import select
import socket

kUnlockTimer = 20
millis = lambda: int(round(time.time() * 1000))

class Coord:
    def __init__(self, y, x):
        self.y = y
        self.x = x

def mqtt_callback(client, userdata, message):
    payload = message.payload
    decoded_payload = ""
    try:
        decoded_payload = payload.decode("utf-8")
    except:
        pass

    parsed_topic = message.topic.split('/')[-1]

    if parsed_topic == "pulse":
        mqtt_manager.register_pulse(decoded_payload)

    if parsed_topic == "motor_requests":
        motor_request = motor_requests_pb2.MotorRequest()
        motor_request.ParseFromString(payload)
        hud_data.throttle = motor_request.throttle
        if motor_request.direction == 2:
            hud_data.throttle_dir = "R "
        else:
            hud_data.throttle_dir = ""

    if parsed_topic == "storage_control":
        if decoded_payload == "unlock0":
            hud_data.payload = "Beginning Unlock Sequence"
            hud_data.unlock = 0
            hud_data.unlock_timer = time.time()

    if parsed_topic == "vitals":
        vitals = vitals_pb2.Vitals()
        vitals.ParseFromString(payload)
        hud_data.battery_level = str(vitals.battery_voltage)[:-1] + "." + str(vitals.battery_voltage)[-1]
        if vitals.payload == "L" and hud_data.payload == "Unlocked":
            hud_data.payload = "Locked"

    if parsed_topic == "cannon_status":
        cannon_status.ParseFromString(payload)

    if parsed_topic == "cannon_prompts":
        prompt_manager.add_prompt(decoded_payload)

    if parsed_topic == "target_color":
        current_target_color = decoded_payload

def voice_callback():
    print("Sending unlock command")
    mqtt_manager.send_message("storage_control", "unlock")


def filter_target_colors(targets, target_color):
    if current_target_color == "All":
        return targets
    else:
        colored_targets = []
        for target in targets:
            if target[0] == target_color:
                colored_targets.append(target)
        return colored_targets


hud_data = hud_pb2.HudPoint()
cannon_status = cannon_pb2.CannonStatus()
prompt_manager = PromptManager()
current_target_color = "All"

mqtt_id = "laptop"
mqtt_targets = ["vision", "wallu", "cannon", "game_master"]
mqtt_targets = ["vision", "cannon", "game_master"]
mqtt_topics = ["motor_requests", "storage_control", "vitals", "cannon_prompts", "cannon_status", "target_color"]
mqtt_manager = mqtt_interface.MqttInterface(id=mqtt_id, targets=mqtt_targets, topics=mqtt_topics, callback=mqtt_callback, alpha=True)
mqtt_manager.start_reading()

#thread = threading.Thread(target=voice_unlock.start_listening, args=("unlock", voice_callback))
#thread.start()

# Set up socket for video streaming
LOCAL_IP = "0.0.0.0"
LOCAL_PORT = 50000

stream_manager = tcp_interface.StreamServer((LOCAL_IP, LOCAL_PORT))
stream_manager.start()

image_hub = imagezmq.ImageHub()

while True:
    if not all(mqtt_manager.target_check(target) for target in mqtt_targets):
        # not ready for normal operation
        print("Waiting for all devices to come online...")
        mqtt_manager.send_message("runtime_config", "0")
        time.sleep(0.5)
        continue
    else:
        mqtt_manager.send_message("runtime_config", "1")

    rpi_name, jpg_buffer = image_hub.recv_jpg()
    image = cv2.imdecode(np.frombuffer(jpg_buffer, dtype='uint8'), -1)
    image = cv2.resize(image, (1920,1080))

    stream_manager.send_frame(np.frombuffer(jpg_buffer, dtype='uint8'))

    if hud_data.unlock == 0:
        if time.time() - hud_data.unlock_timer > 20:
            # Unlock time out
            print("Unlock sequence timed out...")
            mqtt_manager.send_message("storage_control", "unlock2")
            hud_data.payload = "Locked"
            hud_data.unlock = -1

        image, unlock_detected = pose_detect.unlock_pose(image)
        if unlock_detected:
            print("Correct passcode...")
            mqtt_manager.send_message("storage_control", "unlock1")
            hud_data.unlock = 1
            hud_data.payload = "Unlocked"
        

    targets = contour_recognition.target_recognition(image)
    print(len(targets))
    print(targets)
    valid_targets = filter_target_colors(targets, current_target_color)

    for target in valid_targets:
        cv2.drawContours(image, [target[1].astype(int)], -1, (0, 255, 0), 2)

    add_text_overlays(image, hud_data, cannon_status)
    prompt_manager.clear_expired_prompts()
    overlay_prompts(image, prompt_manager.gather_valid_prompts())

    mqtt_manager.send_message("hud_data", hud_data.SerializeToString())

    #cv2.namedWindow(rpi_name, cv2.WND_PROP_FULLSCREEN)
    #cv2.setWindowProperty(rpi_name, cv2.WND_PROP_FULLSCREEN, cv2.WINDOW_FULLSCREEN)
    cv2.imshow(rpi_name, image)
    if cv2.waitKey(1) & 0xFF == ord('q'):
        break
    image_hub.send_reply(b'OK')
