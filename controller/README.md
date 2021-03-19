# WALL-U Controller

## Overview
This directory contains the Python modules that are used to control WALL-U. A breakdown of the modules and their responsibilities are listed below.

| Module | Purpose | Top Level Module |
| ------ | ------- | ---------------- |
| `main_module.py` | Control WALL-U with steering wheel | Yes |
| `cannon.py` | Control WALL-U with steering wheel | Yes |
| `game_master.py` | Choose next target to shoot with speech | Yes |
| `wheel/main_module.py` | Control WALL-U with IMU-based steering wheel | Yes |
| `keyboard_controller.py` | Listen for and send keystrokes over MQTT | No |
| `stream_utils.py` | Provide functions to generate HUD text and image overlays | No |

## Key Decisions
- We decided to integrate several modules (such as `keyboard_controller.py` and `voice_unlock.py`) as subprocesses in response to a strange bug that would arise when integrating them as threads instead. 
- In trying to accomplish distributed processing, we decided to have the different top level modules perform distinct processing and then communicate the results through MQTT, instead of having each module re-perform those processes. For example, only the `game_master.py` module performs contour recognition, and then publishes the contour data through the `target.proto` and `scene.proto` messages.

## Known Bugs
None

## Future Improvements
- Complete the graphical user interface that we started developing to make the startup process simpler for the user

## Attributes
Battery Icons made by <a href="https://www.flaticon.com/authors/freepik" title="Freepik">Freepik</a> from <a href="https://www.flaticon.com/" title="Flaticon"> www.flaticon.com</a>