#!/usr/bin/env python3

# NOTE: this example requires PyAudio because it uses the Microphone class

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
    print("Recognized unlock command")

if __name__ == '__main__':
    print("Main routine, starting...")
    start_listening("unlock", default_callback)