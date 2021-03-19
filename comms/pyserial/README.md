# PySerial Wrapper Library

## Overview
The main purpose of this wrapper library is to provide a threaded implementation of the serial communication package. The Serial package would be used to communicate between the RPIs and Arduinos. We decided that asynchronous I/O would be the best way to go for a more responsive real time system.

## Known Bugs
- On rare occasions, the serial package will be unable to open the port to the Arduino device. The working solution to this bug is to disconnect and reconnect the Arduino's USB cable. Alternatively, since the cable can be hard to access, restarting WALL-U's onboard devices works too.