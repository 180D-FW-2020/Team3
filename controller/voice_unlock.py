import os
import sys
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from comms.mqtt import interface as mqtt_interface
import speech_recognition as sr

def start_listening(keyword, callback):
    # obtain audio from the microphone
    r = sr.Recognizer()

    while True:
        with sr.Microphone(device_index=6) as source:
            try:
                audio = r.listen(source, timeout=2, phrase_time_limit=2)
            except sr.WaitTimeoutError:
                continue
        # recognize speech using Google Speech Recognition
        try:
            # for testing purposes, we're just using the default API key
            # to use another API key, use `r.recognize_google(audio, key="GOOGLE_SPEECH_RECOGNITION_API_KEY")`
            # instead of `r.recognize_google(audio)`
            result = r.recognize_google(audio)
            if keyword in result:
                callback()

        except sr.UnknownValueError:
            pass
        except sr.RequestError as e:
            print(
                "Could not request results from Google Speech Recognition service; {0}".format(e))

def default_callback():
    print("Sending unlock command..")
    mqtt_manager.send_message("storage_control", "unlock")

mqtt_id = "voice_unlock"
mqtt_manager = mqtt_interface.MqttInterface(id=mqtt_id, targets=[], topics=[])
mqtt_manager.start_reading()

start_listening("unlock", default_callback)