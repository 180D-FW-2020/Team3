import serial

class SerialInterface:
    def __init__(self, port, baud=9600, timeout=0):
        self.serial_fd = serial.Serial(port, baudrate=baud, timeout=timeout)
        self.stack = {}
        self.buf = ""

    # To be run by a thread
    def read_from_port(self):
        while True:
            reading = self.serial_fd.readline().decode()
            if reading:
                for char in reading:
                    if char == ";":
                        # Process command in buf
                        self.parse_message(self.buf)
                        self.buf = ""
                    else:
                        self.buf += char

    def single_read(self):
        reading = self.serial_fd.readline().decode()
        if reading:
            for char in reading:
                if char == ";":
                    # Process command in buf
                    self.parse_message(self.buf)
                    self.buf = ""
                else:
                    self.buf += char

    def parse_message(self, message):
        topic = message[:3]
        message = message[3:]
        self.stack[topic] = message

    def write_to_port(self, message):
        self.serial_fd.write(message.encode())
