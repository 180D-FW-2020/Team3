# Cannon

## Overview
This is the cannon Arduino module. It is in its own separate directory due to Arduino's IDE. 

| Module | Device | Purpose |
| ------ | ------ | ------- |
| `cannon.ino` | Arduino | Controls the cannon motors and servos. Listens to Camera Pi for commands.|

## Known Bugs
- Servo buzzes due to not being in the right position after launching a nerf bullet. This issue is due to hardware.

## Future Improvements
- Improve shooting mechanism to avoid servo buzz. 
