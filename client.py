import socket
import numpy as np

class Network:
    def __init__(self):
        self.client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.host = "XXX.XXX.XXX.XXX"
        self.port = 5555
        self.addr = (self.host, self.port)

    def connect(self, name):
        self.client.connect(self.addr)

        # inform server of username
        self.client.send(str.encode(name))

        # receive user ID from server
        val = self.client.recv(8)
        return int(val.decode()) 

    def disconnect(self):
        self.client.close()

    def send(self, keyboard_input):
        try:
            client_msg = keyboard_input.tobytes()
            self.client.send(client_msg)
            reply = bytes()
            while len(reply) < 2688:
                reply += self.client.recv(1024)
            game_world = np.frombuffer(reply, dtype=np.float64).reshape((48, 7))
            return game_world
        except socket.error as e:
            print(e)

