from envs.game_elements import *

import gym
from gym import spaces

import numpy as np

# Création de l'environnement
class TankEnv(gym.Env):
    metadata = {'render.modes': ['human']}

    def __init__(self, max_x, max_y, max_enemies=5, total_ennemies= 10):
        super(TankEnv, self).__init__()
        
        self.max_x = max_x # Largeur de la grille
        self.max_y = max_y # Hauteur de la grille
        self.max_enemies = max_enemies
        self.max_projectiles = max_x * max_y

        self.total_ennemies = total_ennemies

        self.active_ennemies_index = set() # Liste des indices des ennemis actifs dans observation_space["enemies"]

        # Define action space
        self.action_space = spaces.Discrete(6)  # stay, shoot, up, right, down, left
        
        # Define observation space
        self.observation_space = spaces.Dict({
            'player': spaces.Box(low=np.array([0, 0, 0]), high=np.array([self.max_x, self.max_y, 4]), dtype=np.int),  # x, y, direction
            'enemies': spaces.Box(low=np.array([0, 0, 0]), high=np.array([self.max_x, self.max_y, 4]), dtype=np.int, shape=(self.max_enemies, 3)),  # x, y, direction
            'projectiles': spaces.Box(low=np.array([0, 0, 0, 0]), high=np.array([self.max_x, self.max_y, 4, 1]), dtype=np.int, shape=(self.max_projectiles, 4))  # x, y, direction, from (0: player, 1: enemy)
        })

        # Define state
        self.state = {
            'player': Tank(0, 0, np.array([0, 0, 1, 0]), label=0),
            'enemies': {}, # {Tank(0, 0, np.array([0, 0, 1, 0])), Tank(0, 0, np.array([0, 0, 1, 0])), ...}
            'projectiles': {} # {Projectile(0, 0, np.array([0, 0, 1, 0]), label=0), Projectile(0, 0, np.array([0, 0, 1, 0]), label=1), ...}
        }

        self.probability_new_enemy = 0.3

        self.reward_enemy_killed = 1
        self.reward_player_dead = -10
        self.reward_used_projectile = -0.1
        self.reward_nothing = -0.1

        self.done = False
        self.info = {}
        
    def reset(self):
        # initialiser le reward

        # placer le joueur
        ## strat: de manière aléatoire

        # placer les ennemis, attention aux collisions
        ## strat: 3 ennemis de manière aléatoire

        # ne retourne rien
        pass
        
    def step(self, action):
        # Mettre à jour l'état du joueur
        ## strat: en fonction de l'action
        ## reward si l'action est "stay" ou "shoot", 0 sinon

        # Mettre à jour l'état des ennemis
        ## strat: de maniere aleatoire

        # Mettre à jour l'état des projectiles
        ## position et annulation eventuelle

        # Rajouter 1 ennemi si le nombre d'ennemis actifs est inférieur à max_enemies
        ## strat: de manière aléatoire avec une probabilité de self.probability_new_enemy

        # Nettoyer les ennemis tombés
        ## reward_ennemy_killed pour chaque ennemi tombé

        # Verifier si le joueur est mort
        ## le joueur est mort: done = True, reward = reward_player_dead
        ## le joueur n'est pas mort: done = False

        # return new_state, reward, done, False, info= {}

        pass

    def render(self, mode='human'):
        # Créer une matrice R de taille max_x * max_y

        # remplir la matrice avec les éléments de l'environnement
        ## remplir avec le joueur
        ## remplir avec les ennemis
        ## remplir avec les projectiles

        # convert R to frame
        
        # return frame
        pass