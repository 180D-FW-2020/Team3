import serial

class SerialInterface:
    def __init__(self, port, baud=9600, timeout=0):
        self.serial_fd = serial.Serial(port, baudrate=baud, timeout=timeout)
        self.stack = []

    # To be run by a thread
    def read_from_port(self):
        while True:
            reading = self.serial_fd.readline().decode()
            if reading:
                print(reading)

    def parse_message(self, message):
        topic = message[:3]
        message = message[3:]
        self.stack.append([topic, message])

    def inbox_has_message(self):
        return len(stack) > 0

    def write_to_port(self, topic, message):
        msg_str = topic + ":" + message + ";"
        self.serial_fd.write(msg_str.encode())