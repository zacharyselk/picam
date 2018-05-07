#!/usr/bin/python3

# A rudimentary class to transfer data from a client and server

import socket as sock

class InetStream:
    def __init__(self, s):
        # Size of the frame in bytes
        self.MSG_LEN = 0
        if s is None:
            self.socket = sock.socket(sock.AF_INET, sock.SOCK_STREAM)
        else:
            self.socket = s

    def connect(self, host, port):
        self.socket.connect((host, port))

    # Lets the 'server' bind itself to a port and listen for a connnection
    def server(self):
        self.socket.bind('', 1122)
        self.socket.listen(1)

    def accept(self):
        return self.socket.accept()

    # Sends the expected size of 'messages' that will be sent
    def send_len(self, msg_len):
        self.socket.send(str(msg_len).encode('utf-8'))

    # Stores the expected size of 'messages'
    def receive_len(self):
        self.MSG_LEN = int(self.socket.recv(1080))

    # Set the expected size of 'messages'
    def set_msg_len(self, msg_len):
        self.MSG_LEN = msg_len

    # Sends a message to the connected computer
    def write(self, msg):
        total_sent = 0
        while total_sent < self.MSG_LEN:
            sent = self.socket.send(msg[total_sent:])
            if sent == 0:
                break
            #    raise RuntimeError("Socket connection broken")
            total_sent += sent

    # Receives a message from a connected computer
    def receive(self):
        chunks = []
        bytes_recd = 0
        while bytes_recd < self.MSG_LEN:
            chunk = self.socket.recv(min(self.MSG_LEN - bytes_recd, 2048))
            if chunk == b'':
                raise RuntimeError("Socket connection broken")
            chunks.append(chunk)
            bytes_recd = bytes_recd + len(chunk)
        return b''.join(chunks)

    # Closes the connection
    def close(self):
        self.socket.shutdown(1)
        self.socket.close()
