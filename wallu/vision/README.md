# WALL-U Vision

## Overview
The `main_module.py` module in this directory is responsible for streaming the onboard video to the `controller/main_module.py` instance through ImageZMQ. It is also responsible for listening for Cannon commands and passing them along to the Cannon Arduino.

## Key Decisions
- We decided to use a RPI3B to stream video instead of the RPI Zero because we found that the stream quality and latency improved drastically with the added compute. 
- We decided to attach the Cannon Arduino to the Vision RPI because it was easier to assemble that way, and also to avoid potentially exceeding the power allowance of the existing Arduino Nano that was used to control the propulsion motors, storage servos, and storage hall effect sensor.

## Known Bugs
None at this time

## Future Improvements
- Add more cameras to WALL-U to make controlling him more reliable

## Sources
ImageZMQ and image quality code: https://github.com/jeffbass/imagezmq