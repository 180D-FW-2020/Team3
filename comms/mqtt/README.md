# MQTT Wrapper Library

## Overview
The wrapper library here implements a leader-follower protocol that allows a leader device to determine which devices are online at any given time. Follower devices will infinitely send pulse messages at a given frequency as part of the protocol.

## Key Decisions
- We decided that the instance of `controller/main_module.py` would host the MQTT broker to significantly reduce the latency between the steering wheel and WALL-U's onboard RPIs. We then extended network access to the broker within and without the LAN by setting up port forwarding rules and having the address `wallu.ddns.net` reroute to our dynamic public IP address.
- We decided that a hierarchical approach would be better than a peer-to-peer approach in establishing which devices were online, primarily so that one device would be in charge of synchronizing the transition from one dynamic runtime configuration to the next across all devices.

## Known Bugs
None at this time

## Future Improvements
- Dynamically reassign the Leader in the protocol when the `controller/main_module.py` instance is offline. Currently, all devices remain in an idle state until the Leader connects.