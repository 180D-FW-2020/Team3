import os
import sys
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../..')))

import socket
import time
from imutils.video import WebcamVideoStream
import imagezmq
import argparse
from comms.mqtt import interface as mqtt_interface
import time
import cv2
import imutils

ap = argparse.ArgumentParser()
ap.add_argument("-s", "--server-ip", required=True,
                help="ip address of the server to which the client will connect")
args = vars(ap.parse_args())

sender = imagezmq.ImageSender(connect_to="tcp://{}:5555".format(
    args["server_ip"]))

def mqtt_callback(client, userdata, message):
    # Print all messages
    payload = message.payload.decode("utf-8")
    topic = message.topic
    mqtt_manager.pulse_check(topic, payload)
    
    
    print('Received message: "' + payload +
          '" on topic "' + topic + '" with QoS ' + str(message.qos))
    

mqtt_id = "vision"
mqtt_targets = ["laptop"]
mqtt_topics = []
mqtt_manager = mqtt_interface.MqttInterface(id=mqtt_id, targets=mqtt_targets, topics=mqtt_topics, callback=mqtt_callback)
mqtt_manager.start_reading()


while not mqtt_manager.handshake("laptop"):
time.sleep(0.5)


rpi_name = socket.gethostname()  # send RPi hostname with each image
picam = WebcamVideoStream(src=0).start()
#time.sleep(2.0)  # allow camera sensor to warm up
jpeg_quality = 100

while True:  # send images as stream until Ctrl-C
    image = picam.read()
    image = imutils.resize(image, width=480, inter=cv2.INTER_NEAREST)
    ret_code, jpg_buffer = cv2.imencode(".jpg", image, [int(cv2.IMWRITE_JPEG_QUALITY), jpeg_quality])
    sender.send_image(rpi_name, jpg_buffer)

picam.stop()
