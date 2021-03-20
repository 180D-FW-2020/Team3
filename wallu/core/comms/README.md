# Comms

## Overview
These are the files controlling WALL-U's communication with the RPIs. Takes in Serial input and converts them to flags.

| Module | Device | Purpose |
| ------ | ------ | ------- |
| `comms.cpp` | Arduino | Sets flags based on Serial input.|
| `comms.h` | Arduino | Header file for comms.cpp |

## Known Bugs
- `main_module.py` sometimes hands when trying to send vitals from Arduino to RPI. We have found the Serial package to be much more reliable in 1-way communication.

## Future Improvements
- Add more sensors to the onboard RPI and Arduinos, such as proximity sensors, RPM sensors, and a rear view camera.
