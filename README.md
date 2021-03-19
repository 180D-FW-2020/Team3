# WALL-U: Small Robot, Big Dreams

## Objective
The objective of the WALL-U project is to build an immersive robot-control experience with multiple modes of operation. Currently, WALL-U supports payload delivery and multiplayer target shooting with a custom built Nerf Cannon.

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
|__game_master.py
|__cannon.py
|__steering_wheel
   |__main_module.py

comms
|__mqtt
|__pyserial
```
