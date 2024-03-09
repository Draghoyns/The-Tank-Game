from envs.game_elements import *

import gym
from gym import spaces

import matplotlib.pyplot as plt
import numpy as np

# Création de l'environnement
class TankEnv(gym.Env):
    metadata = {'render.modes': ['human']}

    def __init__(self, max_x = 20, max_y = 20, max_enemies_on_screen = 5, total_ennemies_to_kill = 20):
        super(TankEnv, self).__init__()
        
        self.max_x = max_x # Largeur de la grille
        self.max_y = max_y # Hauteur de la grille
        self.max_enemies_on_screen = max_enemies_on_screen
        self.max_projectiles = max_x * max_y

        self.total_ennemies_to_kill = total_ennemies_to_kill
        self.initial_ennemies = 5

        # assertions
        assert max_x > 0
        assert max_y > 0
        assert max_enemies_on_screen > 0
        assert max_enemies_on_screen <= total_ennemies_to_kill
        assert (max_enemies_on_screen + 1) * 9 * 2 <= max_x * max_y 

        # Define action space
        self.action_space = spaces.Discrete(6)  # 0: up, 1: right, 2: down, 3: left, 4: stay, 5: shoot
        
        # Define observation space
        dtypes = np.dtype('int32')
        self.observation_space = spaces.Dict({
            'player': spaces.Box(low=np.array([0, 0, 0]), high=np.array([self.max_x, self.max_y, 4]), dtype=dtypes),  # x, y, direction
            'enemies': spaces.Box(low=np.zeros((self.max_enemies_on_screen, 3), dtype=dtypes), high=np.array([self.max_x, self.max_y, 4] * self.max_enemies_on_screen).reshape(self.max_enemies_on_screen, 3), dtype=dtypes),
            'projectiles': spaces.Box(low=np.zeros((self.max_projectiles, 4), dtype=dtypes), high=np.array([self.max_x, self.max_y, 4, 1] * self.max_projectiles).reshape(self.max_projectiles, 4), dtype=dtypes)  # x, y, direction, from (0: player, 1: enemy)
        })

        # Define state
        self.state = {
            'player': set(),
            'enemies': set(), # (Tank(0, 0, np.array([0, 0, 1, 0])), Tank(0, 0, np.array([0, 0, 1, 0])), ...)
            'projectiles': set() # (Projectile(0, 0, np.array([0, 0, 1, 0]), label=0), Projectile(0, 0, np.array([0, 0, 1, 0]), label=1), ...)
        }

        # Set of all positions occupied by tanks
        self.occupied_positions = set()

        self.probability_new_enemy = 0.3

        self.reward_enemy_killed = 1
        self.reward_player_dead = -10
        self.reward_used_projectile = -0.1
        self.reward_nothing = -0.1

        self.done = False
        self.info = {}
        
    def reset(self):
        self.occupied_positions = set()

        # placer le joueur
        ## strat: de manière aléatoire
        x = np.random.randint(0, self.max_x)
        y = np.random.randint(0, self.max_y)

        direction = np.zeros(4, dtype=int)
        direction[np.random.randint(0, 4)] = 1 # une direction aléatoire

        player = Tank(x, y, direction, label=0)
        self.state['player'] = player

        self.occupied_positions.add((x, y))

        # placer les ennemis, attention aux collisions
        ## strat: self.initial_ennemies ennemis de manière aléatoire
        ennemies = set()
        for i in range(self.initial_ennemies):
            placed = False
            while not placed:
                x = np.random.randint(0, self.max_x)
                y = np.random.randint(0, self.max_y)

                boxes = [(x + i, y + j) for i in range(-2, 3) for j in range(-2, 3)]
                if any(box in self.occupied_positions for box in boxes):
                    continue
                
                direction = np.zeros(4, dtype=int)
                direction[np.random.randint(0, 4)] = 1

                ennemies.add(Tank(x, y, direction, label=1))
                self.occupied_positions.add((x, y))
                placed = True

        self.state['enemies'] = ennemies

        print("#### environnement reset successfully ####")
        
        
    def step(self, action):
        # Mettre à jour l'état du joueur
        ## strat: en fonction de l'action
        ## reward si l'action est "stay" ou "shoot", 0 sinon
        infos = {
            'max_x': self.max_x,
            'max_y': self.max_y,
            'player_position': (self.state['player'].x, self.state['player'].y),
        }
        self.state['player'].update(action, self.occupied_positions, infos)

        # Mettre à jour l'état des ennemis
        ## strat: de maniere aleatoire
        for enemy in self.state['enemies']:
            enemy.update_strategic(self.occupied_positions, infos, strategy=2)

        # Mettre à jour l'état des projectiles
        ## position
        ## annulation des projectiles qui se touchent si necessaire
        ## annulation des projectiles qui sortent de la grille à max_x+1 ou max_y+1

        # Rajouter 1 ennemi si le nombre d'ennemis actifs est inférieur à max_enemies
        ## strat: de manière aléatoire avec une probabilité de self.probability_new_enemy

        # Nettoyer les ennemis tombés
        ## reward_ennemy_killed pour chaque ennemi tombé

        # Verifier si le joueur est mort
        ## le joueur est mort: done = True, reward = reward_player_dead
        ## le joueur n'est pas mort: done = False

        # return new_state, reward, done, info= {}
        return self.state, 0, False, {}

    def render(self, mode='human'):
        # Créer une matrice M de taille max_x * max_y + un padding de 1 de chaque côté
        rows = self.max_y + 2
        cols = self.max_x + 2
        M = np.ones((rows, cols, 3), dtype=np.uint8) * 255 # white background
        # remplir la matrice avec les éléments de l'environnement
        def fill_tank(tank, color):
            # print(f"#### filling tank {tank.coord_and_dir} with color {color} ####")
            x, y, dir, _ = tank.info()
            x += 1 # because of the padding
            y += 1 # because of the padding

            M[y, x] = color 
            if dir in [1, 2]:
                M[y-1, x-1, :] = color
            if dir in [0, 1, 3]:
                M[y-1, x, :] = color
            if  dir in [2, 3]:
                M[y-1, x+1, :] = color
            if dir in [0, 2, 3]:
                M[y, x-1, :] = color
            if dir in [0, 1, 2]:
                M[y, x+1, :] = color
            if dir in [0, 1]:
                M[y+1, x-1, :] = color
            if dir in [1, 2, 3]:
                M[y+1, x, :] = color
            if dir in [0, 3]:
                M[y+1, x+1, :] = color
        ## remplir avec le joueur
        fill_tank(self.state['player'], [0, 255, 0])
                
        ## remplir avec les ennemis
        for enemy in self.state['enemies']:
            fill_tank(enemy, [255, 0, 0])

        ## remplir avec les projectiles
        for projectile in self.state['projectiles']:
            x, y, dir, label = projectile.info
            M[x+1, y+1, :] = [0, 0, 255]

        # return frame
        return M
    
    def plot_render(self):
        M = self.render()
        plt.axis('off')
        plt.imshow(M)
        plt.show()