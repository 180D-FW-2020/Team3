# run this program on each RPi to send a labelled image stream
import socket
import time
from imutils.video import VideoStream
import imagezmq
import argparse

ap = argparse.ArgumentParser()
ap.add_argument("-s", "--server-ip", required=True,
                help="ip address of the server to which the client will connect")
args = vars(ap.parse_args())

sender = imagezmq.ImageSender(connect_to="tcp://{}:5555".format(
    args["server_ip"]))


rpi_name = socket.gethostname()  # send RPi hostname with each image
picam = VideoStream(src=0).start()
time.sleep(2.0)  # allow camera sensor to warm up

while True:  # send images as stream until Ctrl-C
    image = picam.read()
    sender.send_image(rpi_name, image)
