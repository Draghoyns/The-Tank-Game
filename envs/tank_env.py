from envs.game_elements import *

import gym
from gym import spaces

import numpy as np

# Création de l'environnement
class TankEnv(gym.Env):
    metadata = {'render.modes': ['human']}

    def __init__(self):
        super(TankEnv, self).__init__()
        self.action_space = spaces.Discrete(3)
        self.observation_space = spaces.Box(low=0, high=255, shape=(84, 84, 3), dtype=np.uint8)
        # Initialisation de l'état du jeu

    def step(self, action):
        # Implement the step method here
        pass

    def reset(self):
        # Implement the reset method here
        pass

    def render(self, mode='human'):
        # Implement the render method here
        pass

    def close(self):
        # Implement the close method here
        pass

    def test(self):
        print("Test")