import os
import sys
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../..')))

import socket
import time
from imutils.video import WebcamVideoStream
import imagezmq
from comms.mqtt import interface as mqtt_interface
import time
import cv2
import imutils

SERVER_IP = "192.168.1.206"

sender = imagezmq.ImageSender(connect_to="tcp://{}:5555".format(
    SERVER_IP))

def mqtt_callback(client, userdata, message):
    # Print all messages
    payload = message.payload.decode("utf-8")
    topic = message.topic
    mqtt_manager.pulse_check(topic, payload)

    parsed_topic = message.topic.split('/')[-1]
    if parsed_topic == "runtime_config":
        try:
            runtime_config = int(payload.decode("utf-8"))
            print("Set runtime config to " + str(runtime_config))
        except:
            print("Could not parse runtime config, resetting to standby.")
            runtime_config = 0


mqtt_id = "vision"
mqtt_targets = ["laptop"]
mqtt_topics = []
mqtt_manager = mqtt_interface.MqttInterface(id=mqtt_id, targets=mqtt_targets, topics=mqtt_topics, callback=mqtt_callback)
mqtt_manager.start_reading()

# First connect to Controller Main
while runtime_config == 0:
    print("Waiting for instructions from main controller...")
    time.sleep(0.5)

rpi_name = socket.gethostname()  # send RPi hostname with each image
picam = WebcamVideoStream(src=0).start()
#time.sleep(2.0)  # allow camera sensor to warm up
jpeg_quality = 70

while True:  # send images as stream until Ctrl-C
    image = picam.read()
    image = imutils.resize(image, width=480, inter=cv2.INTER_NEAREST)
    ret_code, jpg_buffer = cv2.imencode(".jpg", image, [int(cv2.IMWRITE_JPEG_QUALITY), jpeg_quality])
    sender.send_image(rpi_name, jpg_buffer)

picam.stop()
