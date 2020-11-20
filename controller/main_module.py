import os
import sys
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

import cv2
import imagezmq
import voice_unlock
from comms.mqtt import interface as mqtt_interface
from comms.proto import motor_requests_pb2
import time
import threading


class Coord:
    def __init__(self, y, x):
        self.y = y
        self.x = x


class HudData:
    def __init__(self):
        self.battery_level = 100
        self.speed = 0
        self.throttle = 100
        self.range_finder = "Out of Range"
        self.payload = "Locked"
        self.init_icon_offsets()
        self.load_icons()

    def init_icon_offsets(self):
        self.battery_offset = Coord(y=10, x=40)

    def load_icons(self):
        self.battery_icons = {}
        self.battery_icons["full"] = cv2.imread(
            "graphics/icons/battery/full-battery.png", -1)
        self.battery_icons["almost_full"] = cv2.imread(
            "graphics/icons/battery/battery-almost-full.png", -1)
        self.battery_icons["half_full"] = cv2.imread(
            "graphics/icons/battery/half-battery.png", -1)
        self.battery_icons["low"] = cv2.imread(
            "graphics/icons/battery/low-battery.png", -1)
        self.battery_icons["empty"] = cv2.imread(
            "graphics/icons/battery/empty-battery.png", -1)

        # Resize icons
        scale_percent = 20
        width = int(self.battery_icons["full"].shape[1]*scale_percent / 100)
        height = int(self.battery_icons["full"].shape[0]*scale_percent / 100)
        for level in self.battery_icons:
            self.battery_icons[level] = cv2.resize(
                self.battery_icons[level], (width, height), interpolation=cv2.INTER_AREA)

    def get_battery_icon(self):
        if self.battery_level > 90:
            return self.battery_icons["full"]
        elif self.battery_level > 70:
            return self.battery_icons["almost_full"]
        elif self.battery_level > 40:
            return self.battery_icons["half_full"]
        elif self.battery_level > 20:
            return self.battery_icons["low"]
        else:
            return self.battery_icons["empty"]


def overlay_image(base, layer, offset):
    # Function from https://stackoverflow.com/questions/14063070/overlay-a-smaller-image-on-a-larger-image-python-opencv
    y1, y2 = offset.y, offset.y + layer.shape[0]
    x1, x2 = offset.x, offset.x + layer.shape[1]

    alpha_layer = layer[:, :, 3] / 255.0
    alpha_base = 1.0 - alpha_layer

    for i in range(3):
        base[y1:y2, x1:x2, i] = (
            alpha_layer * layer[:, :, i] + alpha_base * base[y1:y2, x1:x2, i])


def overlay_text(image, text, font_scale, bottom_left, thickness=2):
    cv2.putText(image, text,
                bottom_left,
                cv2.FONT_HERSHEY_COMPLEX_SMALL,
                font_scale,
                (0, 0, 0),
                thickness, 1)


def add_text_overlays(image, hud):
    overlay_text(image, "System Overview", 2,
                 (battery_offset.x, battery_offset.y+150), 3)
    overlay_text(image, "- Speed: " + str(hud.speed) + "m/s", 1.5,
                 (battery_offset.x, battery_offset.y+200))
    overlay_text(image, "- Throttle: " + str(hud.throttle) + "%", 1.5,
                 (battery_offset.x, battery_offset.y+240))
    overlay_text(image, "- Range Finder: " + str(hud.range_finder), 1.5,
                 (battery_offset.x, battery_offset.y+280))
    overlay_text(image, "- Payload Compartment: " + hud.payload, 1.5,
                 (battery_offset.x, battery_offset.y+320))

def mqtt_callback(client, userdata, message):
    # Print all messages
    payload = message.payload
    topic = message.topic
    mqtt_manager.pulse_check(topic, payload.decode("utf-8"))

    '''
    print('Received message: "' + payload +
          '" on topic "' + topic + '" with QoS ' + str(message.qos))
    '''

def voice_callback():
    print("Sending unlock command")
    mqtt_manager.send_message("storage_control", "unlock")

mqtt_id = "laptop"
mqtt_targets = ["vision", "wallu", "wheel"]
mqtt_topics = []
mqtt_manager = mqtt_interface.MqttInterface(id=mqtt_id, targets=mqtt_targets, topics=mqtt_topics, callback=mqtt_callback)
mqtt_manager.start_reading()

# First connect to Wheel Main Pi
print("Opening connection to Steering Wheel Main...")
while not mqtt_manager.handshake("wheel"):
    time.sleep(0.5)

# Then connect to WALL-U Main Pi
print("Opening connection to WALL-U Main...")
while not mqtt_manager.handshake("wallu"):
    time.sleep(0.5)


thread = threading.Thread(target=voice_unlock.start_listening, args=("unlock", voice_callback))
thread.start()

# Then connect to WALL-U Vision Pi
print("Opening connection to WALL-U Vision...")
while not mqtt_manager.handshake("vision"):
    time.sleep(0.5)


image_hub = imagezmq.ImageHub()
hud_data = HudData()
while True:
    rpi_name, image = image_hub.recv_image()

    battery_icon = hud_data.get_battery_icon()
    battery_offset = hud_data.battery_offset
    overlay_image(image, battery_icon, battery_offset)

    add_text_overlays(image, hud_data)

    cv2.namedWindow(rpi_name, cv2.WND_PROP_FULLSCREEN)
    cv2.setWindowProperty(
        rpi_name, cv2.WND_PROP_FULLSCREEN, cv2.WINDOW_FULLSCREEN)
    cv2.imshow(rpi_name, image)
    if cv2.waitKey(1) & 0xFF == ord('q'):
        break
    image_hub.send_reply(b'OK')
