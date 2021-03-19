# WALL-U Communication APIs

## Overview
Low latency, high throughput communication is essential to building a real time distributed system like WALL-U, so we chose to implement our own wrapper libraries around existing packages like MQTT and Serial to optimize for that goal and abstract away the low level details.

| Package     | We Added |
| ----------- | ----------- |
| MQTT        | Runtime configuration system, leader-follower protocol      |
| PySerial    | Threaded implementation for asynchronous I/O        |
| Socket      | Server & Client instances that support frame delimiting and queueing  |
| Protobuf    | Our own `.proto` messages

We also use the ImageZMQ package to stream video from the onboard camera to the `controller/main_module.py` instance, though we did not need to implement a wrapper library for it.
