from envs.game_elements import *

import gym
from gym import spaces

import numpy as np

# Création de l'environnement
class TankEnv(gym.Env):
    metadata = {'render.modes': ['human']}

    def __init__(self, max_x, max_y, max_enemies):
        super(TankEnv, self).__init__()
        
        self.max_x = max_x # Largeur de la grille
        self.max_y = max_y # Hauteur de la grille
        self.max_enemies = max_enemies
        self.max_projectiles = max_x * max_y

        # Define action space
        self.action_space = spaces.Discrete(6)  # stay, shoot, up, right, down, left
        
        # Define observation space
        self.observation_space = spaces.Dict({
            'player': spaces.Box(low=np.array([0, 0, 0]), high=np.array([self.max_x, self.max_y, 4]), dtype=np.int),  # x, y, direction
            'enemies': spaces.Box(low=np.array([0, 0, 0]), high=np.array([self.max_x, self.max_y, 4]), dtype=np.int, shape=(self.max_enemies, 3)),  # x, y, direction
            'projectiles': spaces.Box(low=np.array([0, 0, 0, 0]), high=np.array([self.max_x, self.max_y, 4, 1]), dtype=np.int, shape=(self.max_projectiles, 4))  # x, y, direction, from (0: player, 1: enemy)
        })
        
    def reset(self):
        # Implement the reset method here
        pass

    def step(self, action):
        # Implement the step method here
        pass

    def render(self, mode='human'):
        # Implement the render method here
        pass

    def close(self):
        # Implement the close method here
        pass

    def test(self):
        print("Test")