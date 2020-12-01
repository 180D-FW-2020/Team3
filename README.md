# Team 3

## Objective
The objective of the WALL-U project is to facilitate secure, non-contact payload delivery between two people with a remote controlled robot and an immersive user experience. 

## Software Organization
```
wallu
|__wallu.ino
|__main_module.py
|__voice_recognition.py
|__vision
|  |__main_module.py
|__core
   |__motor
   |  |__motor.**
   |__sensing
      |__sensor.hh

controller
|__main_module.py
|__video_processing.py
|__hud.py
|__steering_wheel
   |__main_module.py

comms
|__mqtt
|__pyserial
```