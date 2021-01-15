import os
import sys
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

import cv2
import imagezmq
#import voice_unlock
from comms.mqtt import interface as mqtt_interface
from comms.proto import motor_requests_pb2
from comms.proto import vitals_pb2
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


class HudData:
    def __init__(self):
        self.battery_level = -1
        self.speed = 0
        self.throttle = 0
        self.throttle_dir = ""
        self.range_finder = "Out of Range"
        self.payload = "Locked"
        self.unlock = -1
        self.unlock_timer = -1

def overlay_text(image, text, font_scale, bottom_left, thickness=2):
    cv2.putText(image, text,
                bottom_left,
                cv2.FONT_HERSHEY_COMPLEX_SMALL,
                font_scale,
                (60, 226, 69),
                thickness, 1)


def add_text_overlays(image, hud):

    kOffsetX = 20
    kOffsetY = 20

    overlay_text(image, "System Overview", 2,
                 (kOffsetX, kOffsetY+150), 3)
    overlay_text(image, "- Battery Level: " + str(hud.battery_level) + "V", 1.5,
                 (kOffsetX, kOffsetY+200))
    overlay_text(image, "- Throttle: " + hud_data.throttle_dir + str(hud.throttle) + "%", 1.5,
                 (kOffsetX, kOffsetY+240))
    overlay_text(image, "- Payload Compartment: " + hud.payload, 1.5,
                 (kOffsetX, kOffsetY+280))

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



def voice_callback():
    print("Sending unlock command")
    mqtt_manager.send_message("storage_control", "unlock")

hud_data = HudData()

mqtt_id = "laptop"
mqtt_targets = ["vision", "wallu", "cannon"]
mqtt_targets = ["vision", "cannon"]
mqtt_topics = ["motor_requests", "storage_control", "vitals"]
mqtt_manager = mqtt_interface.MqttInterface(id=mqtt_id, targets=mqtt_targets, topics=mqtt_topics, callback=mqtt_callback, alpha=True)
mqtt_manager.start_reading()

#thread = threading.Thread(target=voice_unlock.start_listening, args=("unlock", voice_callback))
#thread.start()

def accept_upd_conns():
    try:
        conn, client_addr = tcp_socket.accept()
        tcp_conns.append(conn)
        print("New connection from " + str(client_addr))
    except:
        pass

# Set up socket for video streaming
LOCAL_IP = "0.0.0.0"
LOCAL_PORT = 50000
BUFFER_SIZE = 10240

tcp_socket = socket.socket(family=socket.AF_INET, type=socket.SOCK_STREAM)
tcp_socket.setblocking(0)
tcp_socket.bind((LOCAL_IP, LOCAL_PORT))
tcp_socket.listen(5)
tcp_conns = []

image_hub = imagezmq.ImageHub()

while True:
    accept_upd_conns()
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

    for conn in tcp_conns:
        try:
            conn.sendall(jpg_buffer)
        except:
            print("bad write :(")
            print(sys.exc_info()[0])

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
        

    add_text_overlays(image, hud_data)

    #cv2.namedWindow(rpi_name, cv2.WND_PROP_FULLSCREEN)
    #cv2.setWindowProperty(rpi_name, cv2.WND_PROP_FULLSCREEN, cv2.WINDOW_FULLSCREEN)
    cv2.imshow(rpi_name, image)
    if cv2.waitKey(1) & 0xFF == ord('q'):
        break
    image_hub.send_reply(b'OK')
