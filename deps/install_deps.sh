#!/usr/bin/bash

# this script creates a virtual environment so the following installs don't
# fuck with your previous installs <3

echo "Installing WALL-U Dependencies"
pip install opencv-contrib-python
pip install imutils
pip installl SpeechRecognition
pip install pyaudio
pip install protobuf 
pip install pynput
pip install paho-mqtt
pip install imagezmq
pip install numpy
