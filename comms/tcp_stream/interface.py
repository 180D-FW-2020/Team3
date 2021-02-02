import socket
import time
import threading
import sys
import numpy as np

kBufferSize = 8192

class StreamClient:
    def __init__(self, server_info):
        self.tcp_client = socket.socket(family=socket.AF_INET, type=socket.SOCK_STREAM)
        self.frame_init = False
        self.buffer = "".encode()
        self.connected = False

        while not self.connected:
            try:
                self.tcp_client.connect(server_info)
                self.connected = True
            except:
                print("Could not connect to stream...")
                time.sleep(0.5)
        
    def read_frames(self):
        while True:
            jpg_buffer = self.tcp_client.recv(kBufferSize)
            if "eve".encode() in jpg_buffer:
                delim = jpg_buffer.split("eve".encode())
                full_frame = self.buffer + delim[0]
                full_frame = np.frombuffer(full_frame, dtype='uint8')
                self.frame = full_frame
                self.buffer = delim[-1]
                self.frame_init = True
            else:
                self.buffer += jpg_buffer

    def start(self):
        client_thread = threading.Thread(target=self.read_frames)
        client_thread.start()

class StreamServer:
    def __init__(self, local_info, max_conns=5):
        self.tcp_socket = socket.socket(family=socket.AF_INET, type=socket.SOCK_STREAM)
        self.tcp_socket.setblocking(0)
        self.tcp_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        self.tcp_socket.bind(local_info)
        self.tcp_socket.listen(max_conns)
        self.tcp_conns = []

    def accept_new_conns(self):
        while True:
            try:
                conn, client_addr = self.tcp_socket.accept()
                self.tcp_conns.append(conn)
                print("New connection from " + str(client_addr))
            except:
                pass

    def start(self):
        server_thread = threading.Thread(target=self.accept_new_conns)
        server_thread.start()

    def send_frame(self, buffer):
        for conn in self.tcp_conns:
            try:
                conn.sendall(buffer)
                conn.sendall("eve".encode())
            except Exception as e:
                print("Bad stream write...")
                print(e)
                print(sys.exc_info()[0])
