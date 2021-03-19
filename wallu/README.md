# WALL-U

## Overview
All files for the onboard RPI and Arduino are in this directory. The division of processing responsibilities are listed below.

| Module | Device | Purpose |
| ------ | ------ | ------- |
| `main_module.py` | RPI | Listen for MQTT throttle, storage messages and pass them along to Arduino|
| `wallu.ino` | Arduino | Accept and execute throttle, servo commands, actuate eye lights based on state |

## Known Bugs
- `main_module.py` sometimes hands when trying to send vitals from Arduino to RPI. We have found the Serial package to be much more reliable in 1-way communication.

## Future Improvements
- Add more sensors to the onboard RPI and Arduinos, such as proximity sensors, RPM sensors, and a rear view camera.
