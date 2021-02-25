import os
import sys
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from comms.mqtt import interface as mqtt_interface
import speech_recognition as sr
import argparse

def start_listening(keywords, callback):
    # obtain audio from the microphone
    r = sr.Recognizer()

    while True:
        with sr.Microphone(device_index=mic_index) as source:
            try:
                print("reached")
                audio = r.listen(source, phrase_time_limit=3)
            except sr.WaitTimeoutError:
                continue
        # recognize speech using Google Speech Recognition
        try:
            # for testing purposes, we're just using the default API key
            # to use another API key, use `r.recognize_google(audio, key="GOOGLE_SPEECH_RECOGNITION_API_KEY")`
            # instead of `r.recognize_google(audio)`
            result = r.recognize_google(audio)
            for keyword in keywords:
                if keyword in result:
                    callback(keyword)

        except sr.UnknownValueError:
            pass
        except sr.RequestError as e:
            print(
                "Could not request results from Google Speech Recognition service; {0}".format(e))

def dumb_callback(client, userdata, message):
    pass

def default_callback(keyword):
    valid_colors = ["red", "blue", "green"]
    
    if (keyword == "unlock"):
        print("Sending unlock command..")
        mqtt_manager.send_message("storage_control", "unlock0")

    if (keyword in valid_colors):
        print("Sending color...")
        mqtt_manager.send_message("target_color", keyword)

parser = argparse.ArgumentParser()
parser.add_argument("mqtt_id", type=str, help="MQTT ID")
parser.add_argument("--local", help="Connect to stream over LAN", action="store_true")
parser.add_argument("--mic_index", help="choose a custom mic index (default 0)")
args = parser.parse_args()

mqtt_id = args.mqtt_id
mqtt_manager = mqtt_interface.MqttInterface(id=mqtt_id, targets=[], topics=[], callback = dumb_callback, local=True if args.local else False)
mqtt_manager.start_reading()

if args.mic_index:
    mic_index = int(args.mic_index)
else:
    mic_index = 0

print("Using mic index " + str(mic_index))

keywords = ["red", "blue", "reset"]
start_listening(keywords, default_callback)