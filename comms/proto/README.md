# Protobuf Messages

## Overview
We chose to add Google Protobuf messages to our technology stack because they are easy to add, serialize, and parse. The message formats are defined in the `.proto` files, and then they are compiled into `_pb2.py` Python classes using the `proto3` compiler. 

## Known Bugs
None. Just remember to recompile any messages after changing them!