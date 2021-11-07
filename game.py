import pygame
import numpy as np
from client import Network
import time

class PlayerClient:
    def __init__(self, W=800, H=600):
        self.screen = pygame.display.set_mode((W, H))
        pygame.display.set_caption("PyTanks")

        self.get_player_name()
        self.join_server()
        self.run_game()
        self.quit_game()

    def get_player_name(self):
        self.name = ""
        while not (0 < len(self.name) < 20):
            self.name = input("Please enter your name: ")

    def join_server(self):
        self.server = Network()
        self.ID = self.server.connect(self.name)
        self.running = True
        print("Connected to server, player ID:", self.ID)

    def run_game(self):
        clock = pygame.time.Clock()
        while self.running:
            clock.tick(30)
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    self.running = False

            # [W, A, S, D, space]
            keyboard_input = np.zeros(5, dtype=bool)
            keys = pygame.key.get_pressed()
            if keys[pygame.K_UP] or keys[pygame.K_w]:
                keyboard_input[0] = 1
            if keys[pygame.K_LEFT] or keys[pygame.K_a]:
                keyboard_input[1] = 1
            if keys[pygame.K_DOWN] or keys[pygame.K_s]:
                keyboard_input[2] = 1
            if keys[pygame.K_RIGHT] or keys[pygame.K_d]:
                keyboard_input[3] = 1
            if keys[pygame.K_SPACE]:
                keyboard_input[4] = 1
            if keys[pygame.K_ESCAPE]:
                self.running = False

            game_world = self.server.send(keyboard_input)
            self.render(game_world)

    def render(self, game_world):
        self.screen.fill((0,0,0))
        for i in range(8):
            if game_world[i, 0] == 0:
                continue

            color = (255, 0, 0)
            if i == self.ID:
                    color = (0, 0, 255)
            pygame.draw.circle(self.screen, color, (int(game_world[i, 1]), int(game_world[i, 2])), 25)
            pygame.draw.line(self.screen, (0, 255, 0), ((int(game_world[i, 1]), int(game_world[i, 2]))), ((int(game_world[i, 1] + 25*np.cos(game_world[i, 3])), int(game_world[i, 2] + 25*np.sin(game_world[i, 3])))), 2)
        
        for i in range(8, 48):
            if game_world[i, 0] == 0:
                continue
            pygame.draw.circle(self.screen, (255, 255, 255), (int(game_world[i, 1]), int(game_world[i, 2])), 2)

        pygame.display.update()


    def quit_game(self):
        self.server.disconnect()
        pygame.quit()
        quit()
	

if __name__ == "__main__":
    pygame.init()
    player_client = PlayerClient()