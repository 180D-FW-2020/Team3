import threading
from serial_threaded import SerialInterface

# Instantiate Serial Interface
serial_interface = SerialInterface("/dev/tty.usbmodem146201")

# Start listening on thread
thread = threading.Thread(target=serial_interface.read_from_port)
thread.start()

# Spin
while True:
    pass # Wait for messages
