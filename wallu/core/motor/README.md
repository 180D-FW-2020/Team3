# Motor

## Overview
These libraries control the motor functionality, including ramp and various protection.

| Module | Device | Purpose |
| ------ | ------ | ------- |
| `motor.*` | Arduino | Controls ramp and maintains information on the motor.|
| `motor_control.*` | Arduino | Controls what throttle & angle gets inputted into motor control.|
| `sensing` | Arduino | Reads sensor data|

## Known Bugs
- Backwards movement only has one direction, cannot turn.

## Future Improvements
- Add speed adjustments to WALL-U on the go.
- Add RPM sensors in order to control speed (PID).
