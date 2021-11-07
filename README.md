# PyTanks
This project started as a one day project with two goals:
- Create a simulated environment with as much logic as possible written in Numpy, to open the possibility of using it as a training ground for Reinforcement Learning.
- Learn the basics of creating servers and clients in Python using the "socket" and "threading" modules.

### Requirements
- numpy
- socket
- threading
- pygame
- time

### How to run
To start the server: `$ python server.py`

Once the server has started, it will print the serer IP into the terminal, this must be enterred into `client.py` in order for clients to find the server.

To start the game: `$ python game.py`

Once the game starts, you will be prompted to enter a username in the terminal (max 20 characters). Once enterred, this will be sent to the server and the player will be connected. The server supports a maximum of 8 players. Controls are WASD for movement and SPACE to fire projectiles.
