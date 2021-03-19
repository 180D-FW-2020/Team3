# WALL-U TCP Stream

## Overview
The purpose of this wrapper library is to abstract away the low level details of socket networking. We need to use socket networking to extend the video stream to viewers within and outside of the LAN because ImageZMQ streams video _to_ a server, and not from, which makes the stream harder to extend. 

## Key Decisions
- We decided to implement our own frame delimiters (which we chose to be the string `"eve"`) because it would be more efficient to send the image frames in smaller segments than to try and send entire image frames in one go.
- We decided to use TCP instead of UDP because we opted for reliability in the stream over minimal latency gains. We also found it easier to manage TCP connections than it was to use a connection-less protocol like UDP.

## Known Bugs
None at this time

## Future Improvements
- Transition to a UDP-based stream to fully optimize for latency. This might require a kind of out-of-band MQTT channel to manage connection metadata. 