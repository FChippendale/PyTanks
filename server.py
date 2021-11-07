import socket
import threading
import time
import numpy as np
import pygame

class Server:
    def __init__(self):
        PORT = 5555
        if not self._start_server(PORT):
            return

        self.setup_game()

        thread = threading.Thread(target=self.add_players, daemon=True)
        thread.start()

        self.run_game()

    def _start_server(self, PORT):
        self.server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)

        HOST_NAME = socket.gethostname()
        SERVER_IP = socket.gethostbyname(HOST_NAME)

        try:
            self.server_socket.bind((SERVER_IP, PORT))
        except socket.error as e:
            print(str(e))
            print("[SERVER] Server could not start")
            return False

        self.server_socket.listen()

        print(f"[SERVER] Server Started with local ip {SERVER_IP}")
        return True

    def setup_game(self):
        self.player_count = 0

        # is_alive; x; y; theta; v; omega; info
        # for tanks, info = score
        # for bullets, info = distance travelled
        self.world_data = np.zeros((48, 7), dtype=np.float64)
        self.player_inputs = np.zeros((8, 5), dtype=np.int32)

        TANK_V = 3.0
        TANK_OMEGA = 0.04
        BULLET_V = 10.0

        self.world_data[:8, 4] = TANK_V
        self.world_data[:8, 5] = TANK_OMEGA
        self.world_data[8:, 4] = BULLET_V

    def run_game(self):
        MAX_BULLET_DIST = 1200

        clock = pygame.time.Clock()
        while True:
            clock.tick(60)
            self.world_data[:8, 3] += (self.player_inputs[:, 3] - self.player_inputs[:, 1]) * self.world_data[:8, 5]
            self.world_data[:8, 1] += (self.player_inputs[:, 0] - self.player_inputs[:, 2]) * np.cos(self.world_data[:8, 3]) * self.world_data[:8, 4]
            self.world_data[:8, 2] += (self.player_inputs[:, 0] - self.player_inputs[:, 2]) * np.sin(self.world_data[:8, 3]) * self.world_data[:8, 4]

            self.world_data[8:, 1] += np.cos(self.world_data[8:, 3]) * self.world_data[8:, 4]
            self.world_data[8:, 2] += np.sin(self.world_data[8:, 3]) * self.world_data[8:, 4]

            self.world_data[8:, 5] += self.world_data[8:, 4] * self.world_data[8:, 0]
            self.world_data[8:, 0] = np.where(self.world_data[8:, 5] > MAX_BULLET_DIST, 0, 1)

            # create bullets
            shooting_id = np.where(self.player_inputs[:, 4] == 1)[0]
            for idx in shooting_id:
                id = idx * 5 + 8
                free_slots = np.where(self.world_data[id:id+5, 0] == 0)[0]
                if len(free_slots) > 0:
                    bullet_index = free_slots[0]
                    self.world_data[id+bullet_index, 0] = 1
                    self.world_data[id+bullet_index, 1] = self.world_data[idx, 1] + np.cos(self.world_data[idx, 3]) * 30
                    self.world_data[id+bullet_index, 2] = self.world_data[idx, 2] + np.sin(self.world_data[idx, 3]) * 30
                    self.world_data[id+bullet_index, 3] = self.world_data[idx, 3]
                    self.world_data[id+bullet_index, 5] = 0

            # detect collisions
            for i in range(8):
                if self.world_data[i, 0] == 0:
                    continue
                if np.count_nonzero(np.linalg.norm(self.world_data[self.world_data[:, 0] == 1][:, 1:3] - self.world_data[i, 1:3], axis=1) < 25) > 1:
                    self.respawn(i)

    def respawn(self, tank_index):
        self.world_data[tank_index, 1] = np.random.randint(800)
        self.world_data[tank_index, 2] = np.random.randint(600)

    def add_players(self):
        while True:
            conn, address = self.server_socket.accept()

            available_ids = np.where(self.world_data[:8, 0] == 0)[0]
            if len(available_ids) == 0:
                print("server full")
                continue

            thread = threading.Thread(target=self.player_handler, args=(conn, available_ids[0]), daemon=True)
            thread.start()
            self.player_count += 1
            

    def player_handler(self, conn, player_id):
        data = conn.recv(16)
        name = data.decode("utf-8")
        print("[LOG]", name, "connected to the server.")

        conn.send(str.encode(str(player_id)))
        self.world_data[player_id, 0] = 1
        self.respawn(player_id)

        while True:
            data = conn.recv(5)
            if not data:
                self.world_data[player_id, 0] = 0
                break

            player_input = np.frombuffer(data, dtype=bool)
            self.player_inputs[player_id] = player_input.astype(int)
            conn.send(self.world_data.tobytes())


            

a = Server()
print("program concluded")