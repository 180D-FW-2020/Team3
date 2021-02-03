import os
import sys
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from comms.mqtt import interface as mqtt_interface
import speech_recognition as sr

def start_listening(keywords, callback):
    # obtain audio from the microphone
    r = sr.Recognizer()

    while True:
        with sr.Microphone() as source:
            try:
                print("Listening")
                audio = r.listen(source, phrase_time_limit=4)
            except sr.WaitTimeoutError:
                continue
        # recognize speech using Google Speech Recognition
        try:
            # for testing purposes, we're just using the default API key
            # to use another API key, use `r.recognize_google(audio, key="GOOGLE_SPEECH_RECOGNITION_API_KEY")`
            # instead of `r.recognize_google(audio)`
            result = r.recognize_google(audio)
            print(result)
            for keyword in keywords:
                if keyword in result:
                    callback(keyword)

        except sr.UnknownValueError:
            pass
        except sr.RequestError as e:
            print(
                "Could not request results from Google Speech Recognition service; {0}".format(e))

def default_callback(keyword):
    valid_colors = ["red", "blue"]
    if keyword == "unlock":
        print("Sending unlock command..")
        mqtt_manager.send_message("storage_control", "unlock0")
    if keyword in valid_colors:
        print("Sending color..")
        mqtt_manager.send_message("target_color", keyword)
    if keyword == "reset" or keyword == "restart":
        print("Sending 'All'..")
        mqtt_manager.send_message("target_color", "All")

mqtt_id = "voice_unlock"
mqtt_manager = mqtt_interface.MqttInterface(id=mqtt_id, targets=[], topics=[])
mqtt_manager.start_reading()

keywords = ["unlock", "red", "blue", "restart", "reset"]
start_listening(keywords, default_callback)
