import numpy as np  # type: ignore
import math
import gym  # type: ignore
import pygame  # type: ignore
import matplotlib.pyplot as plt  # type: ignore
from gym import spaces  # type: ignore

from envs.game_elements import Tank
from utils.coloring import green, yellow, black, turquoise, red
from utils.coloring import fill_tank, fill_obstacle, fill_projectile
from envs.tank_env import TankEnv
from game_play import main as game_main


class Move(object):
    def __init__(self, label, dir, action, x0, y0):
        """
        label: side of the tank (0: green, 1: yellow) (default player is green)
        dir: direction of the tank, list where the direction =1 (0: left, 1: down, 2: right, 3: up)
        action: (0: up, 1: right, 2: down, 3: left, 4: stay, 5: shoot)
        x0: x coordinate of the tank before the move
        y0: y coordinate of the tank before the move
        """
        self.label = label
        self.dir = dir
        self.action = action
        self.x = x0
        self.y = y0

    def valid(self, board):
        # Check if the move is valid on the given board
        # boolean

        # the board contains the occupied positions
        # the move is valid if the bounding box of the tank after the move is
        # not occupied or out of bounds

        if self.action in [4, 5]:
            return True

        # if the direction and the action don't align, the direction changes
        if np.argmax(self.dir) != self.action:
            return True
        else:
            # get the new positions
            new_x = self.x + self.dir[1] - self.dir[3]  # right - left
            new_y = self.y + self.dir[2] - self.dir[0]  # down - up

            # out of bounds ?
            if new_x < 0 or new_x >= board.max_x or new_y < 0 or new_y >= board.max_y:
                return False

            # occupied ?
            boxes = [(new_x + i, new_y + j) for i in range(-2, 3) for j in range(-2, 3)]

            if any(box in board.occupied_positions for box in boxes):
                return False

    def code(self) -> int:
        # Return the code of the move

        # the code is a 4 digit number, where the first digit is the label,
        # the second is the direction, the third is the action,
        # and the last is a hash of the position (x, y)

        code = (
            self.label * 1000
            + np.argmax(self.dir) * 100
            + self.action * 10
            + (self.x * self.y) % 10
        )
        return code


class Board(gym.Env):
    def __init__(
        self,
        max_x=20,
        max_y=20,
        max_enemies_on_screen=5,
        total_ennemies_to_kill=20,
        obstacles="",
        mode="1p",  # 1p or 2p
    ):
        # global settings
        self.mode = mode  # 1p or 2p
        self.max_x = max_x  # Width of grid
        self.max_y = max_y  # Height of grid
        self.max_enemies_on_screen = max_enemies_on_screen
        self.max_projectiles = max_x * max_y
        self.action_space = spaces.Discrete(6)

        # game settings
        self.total_ennemies_to_kill = total_ennemies_to_kill
        self.initial_ennemies = 2
        self.probability_new_enemy = 0.01
        self.obstacles = obstacles

        # 2p setting
        self.turn = "player"  # player or enemy

        # score settings
        self.reward_enemy_killed = 10
        self.reward_player_dead = -20
        self.reward_used_projectile = -0.1
        self.reward_nothing = -0.02
        self.timestep = -0.001

        # assertions
        assert max_x > 0
        assert max_y > 0
        assert max_enemies_on_screen > 0
        assert max_enemies_on_screen <= total_ennemies_to_kill
        assert (max_enemies_on_screen + 1) * 9 * 2 <= max_x * max_y

        # initialization

        self.state = {
            "player": Tank(0, 0, np.array([0, 0, 1, 0])),  # initializing
            "enemies": set(),  # (Tank(0, 0, np.array([0, 0, 1, 0])), Tank(0, 0, np.array([0, 0, 1, 0])), ...)
            "projectiles": set(),  # (Projectile(0, 0, np.array([0, 0, 1, 0]), label=0), Projectile(0, 0, np.array([0, 0, 1, 0]), label=1), ...)
            "obstacles": set(),
            "enemy": Tank(
                0, 0, np.array([0, 0, 1, 0])
            ),  # incompatble with player but will be overridden
        }
        self.occupied_positions = set()

        self.done = False
        self.info = {}

    def reset(self, initial_run=True, seed=None, options=None):
        self.occupied_positions = set()
        self.done = False

        # __________PLAYER__________#
        # place the player randomly
        if initial_run:
            x = np.random.randint(0, self.max_x)
            y = np.random.randint(0, self.max_y)

            direction = np.zeros(4, dtype=int)
            direction[np.random.randint(0, 4)] = 1  # random direction

            player = Tank(x, y, direction, label=0)
            self.state["player"] = player

            self.occupied_positions.add((x, y))

        else:
            self.occupied_positions.add(
                (self.state["player"].x, self.state["player"].y)
            )

        # __________Obstacles__________#
        ## strategy: random

        obstacles = set()
        if self.obstacles == "low":
            nb_obstacles = self.max_x * self.max_y // 80
        elif self.obstacles == "high":
            nb_obstacles = self.max_x * self.max_y // 20
        else:
            nb_obstacles = 0
        if nb_obstacles > 1:
            for i in range(nb_obstacles):
                placed = False
                while not placed:
                    x = np.random.randint(0, self.max_x)
                    y = np.random.randint(0, self.max_y)

                    boxes = [(x + i, y + j) for i in range(-2, 3) for j in range(-2, 3)]

                    if any(box in self.occupied_positions for box in boxes):
                        continue

                    direction = np.zeros(4, dtype=int)
                    direction[np.random.randint(0, 4)] = 1

                    obstacles.add((x, y))
                    self.occupied_positions.add((x, y))
                    placed = True

        self.state["obstacles"] = obstacles

        # ___________Enemies__________#
        # place enemies, beware of collisions

        if self.mode == "2p":
            self.initial_ennemies = 1
            self.max_enemies_on_screen = 1  # fight for the same enemy
            self.total_ennemies_to_kill = 1

        ## strat: self.initial_ennemies random ennemies
        enemies = set()
        for i in range(self.initial_ennemies):
            placed = False
            while not placed:
                x = np.random.randint(0, self.max_x)
                y = np.random.randint(0, self.max_y)

                direction = np.zeros(4, dtype=int)
                direction[np.random.randint(0, 4)] = 1

                enemy = Tank(x, y, direction, label=1)
                boxes = enemy.big_bounding_box()
                if any(box in self.occupied_positions for box in boxes):
                    continue

                enemies.add(enemy)
                self.occupied_positions.add((x, y))
                placed = True

        self.state["enemies"] = enemies

        if self.mode == "2p":
            enemy = self.state["enemy"]

            placed = False
            while not placed:
                x = np.random.randint(0, self.max_x)
                y = np.random.randint(0, self.max_y)

                direction = np.zeros(4, dtype=int)
                direction[np.random.randint(0, 4)] = 1

                enemy = Tank(x, y, direction, label=2)
                boxes = enemy.big_bounding_box()
                if any(box in self.occupied_positions for box in boxes):
                    continue

                self.occupied_positions.add((x, y))
                placed = True

            self.state["enemy"] = enemy

        # __________COHERENCE__________#
        # if the player is stuck, we reset
        # stuck = more than 3 obstacles around the player
        boxes = self.state["player"].big_bounding_box()
        obstacles_around_player = [box for box in boxes if box in obstacles]
        if len(obstacles_around_player) > 3:
            print("#### player is stuck, resetting ####")
            self.reset()
        # else:
        #  print("#### environnement reset successfully ####")

        self.state["player"].score = 0
        self.state["enemy"].score = 0

    def legalMoves(self):
        # set of possible moves
        # list of Move objects
        moves = []
        for action in range(6):
            # check if the move is valid
            x, y, direction, label = self.state[self.turn].info()
            dir = [0, 0, 0, 0]
            dir[direction] = 1
            move = Move(label, dir, action, x, y)
            if move.valid(self):
                moves.append(move)

        return moves

    def score(self) -> dict[str, float]:
        # current score of the player
        if self.mode == "1p":
            return {
                "p1": self.state["player"].score
            }  # to be sure but normally self.turn doesn't change in 1p mode
        else:
            return {"p1": self.state["player"].score, "p2": self.state["enemy"].score}

    def terminal(self) -> bool:
        # check if the game is over
        # if the player is dead, the game is over
        # if the player has killed all the enemies, the game is over

        return self.done

    def step(self, action):
        return self.play(action)

    def play(self, move):

        # play the move on the board
        if type(move) == int:
            action = move
        else:
            action = move.action

        reward = self.timestep  # to avoid inaction

        player = self.turn
        eni = ["enemy" if self.turn == "player" else "player"][0]

        # debugging
        kill_player = self.state[player].kills

        ## canceling projectiles that touch each other if necessary
        # in theory it works, in practice there is some bug
        projectiles = list(self.state["projectiles"])
        for i in range(len(projectiles)):
            for j in range(i + 1, len(projectiles)):
                if (
                    projectiles[i].x == projectiles[j].x
                    and projectiles[i].y == projectiles[j].y
                    and projectiles[i].label != projectiles[j].label
                ):
                    # same position, different players
                    try:
                        self.state["projectiles"].remove(projectiles[i])
                        self.state["projectiles"].remove(projectiles[j])
                    except:
                        pass

        # Add 1 enemy if the number of active enemies is less than max_enemies
        ## strategy: randomly with a probability of self.probability_new_enemy
        # only valid when playing 1p
        if (
            len(self.state["enemies"]) < self.max_enemies_on_screen
            and np.random.rand() < self.probability_new_enemy
        ) or len(self.state["enemies"]) == 0:
            placed = False
            while not placed:
                eni_x = np.random.randint(0, self.max_x)
                eni_y = np.random.randint(0, self.max_y)

                direction = np.zeros(4, dtype=int)
                direction[np.random.randint(0, 4)] = 1

                enemy = Tank(eni_x, eni_y, direction, label=1)

                boxes = enemy.big_bounding_box()
                if any(box in self.occupied_positions for box in boxes):
                    continue

                self.state["enemies"].add(enemy)
                self.occupied_positions.add((eni_x, eni_y))
                placed = True

        # Clean up defeated enemies and used projectiles
        obstacle_boxes = []
        for obstacle in list(self.state["obstacles"]):
            boxes = [
                (obstacle[0] + i, obstacle[1] + j)
                for i in range(-1, 2)
                for j in range(-1, 2)
            ]
            obstacle_boxes += boxes

        # remove the projectiles that touch the obstacles
        for projectile in list(self.state["projectiles"]):
            if (projectile.x, projectile.y) in obstacle_boxes:
                self.state["projectiles"].remove(projectile)

        # remove killed enemies
        ## reward_enemy_killed for each defeated enemy
        for enemy in list(self.state["enemies"]):
            enemy_boxes = enemy.bounding_box()
            for projectile in list(self.state["projectiles"]):

                if (
                    projectile.x,
                    projectile.y,
                ) in enemy_boxes and projectile.label == self.state[player].label:
                    self.state["enemies"].remove(enemy)
                    self.occupied_positions.remove((enemy.x, enemy.y))
                    self.state["projectiles"].remove(projectile)
                    self.state[player].kills += 1
                    self.state[player].score += self.reward_enemy_killed

                    # print("#### player killed an enemy ####")
                    break

                if self.mode == "2p":
                    if (
                        projectile.x,
                        projectile.y,
                    ) in enemy_boxes and projectile.label == self.state[eni].label:
                        self.state["projectiles"].remove(projectile)
                        self.state["enemies"].remove(enemy)
                        self.occupied_positions.remove((enemy.x, enemy.y))
                        self.state[eni].kills += 1
                        self.state[eni].score += self.reward_enemy_killed

                        # print("#### other player killed an enemy ####")
                        break

        # Check if the player is dead
        ## if the player is dead: done = True, reward = reward_player_dead
        ## if the player is not dead: done = False
        boxes = self.state[player].bounding_box()
        boxes_eni = self.state[eni].bounding_box()
        ennemies_projectiles_positions = []
        player_projectiles_positions = []
        eni_projectiles_positions = []

        for projectile in list(self.state["projectiles"]):
            if projectile.label == 1:  # enemies projectile
                ennemies_projectiles_positions.append(projectile)
            if projectile.label == self.state[player].label:
                player_projectiles_positions.append(projectile)  # player projectile
            if projectile.label == self.state[eni].label:
                eni_projectiles_positions.append(projectile)

        # check if the player is dead
        for projectile in ennemies_projectiles_positions + eni_projectiles_positions:
            if (projectile.x, projectile.y) in boxes:
                self.state["projectiles"].remove(projectile)
                self.state[player].score += self.reward_player_dead
                self.state[player].deaths += 1

                if projectile.label == self.state[eni].label:
                    self.state[eni].score += self.reward_enemy_killed
                    self.state[eni].kills += 1
                # print("#### player is dead ####")
                # self.reset(initial_run=False)
                self.done = True
        # check if the enemy is dead
        for projectile in player_projectiles_positions + eni_projectiles_positions:
            if (projectile.x, projectile.y) in boxes_eni:
                self.state["projectiles"].remove(projectile)
                self.state[eni].deaths += 1
                self.state[eni].score += self.reward_player_dead
                if projectile.label == self.state[player].label:
                    self.state[player].kills += 1
                    self.state[player].score += self.reward_enemy_killed
                # print("#### other player is dead ####")
                self.done = True

        if self.state[player].kills >= self.total_ennemies_to_kill:
            self.done = True

        ##################### update #####################

        # Update the player's state
        ## strategy: based on the action
        ## reward if the action is "stay" or "shoot", 0 otherwise
        boundaries = {
            "max_x": self.max_x,
            "max_y": self.max_y,
        }
        self.occupied_positions = self.state[player].update(
            action, self.state, self.occupied_positions, boundaries
        )
        if action == 4:
            reward += self.reward_nothing
        elif action == 5:
            reward += self.reward_used_projectile

        # Update the state of enemies
        ## strategy: random
        for enemy in self.state["enemies"]:
            self.occupied_positions = enemy.update_strategic(
                self.state, self.occupied_positions, boundaries, strategy=2
            )

        # Update the state of projectiles
        ## position
        for projectile in list(
            self.state["projectiles"]
        ):  # list() to avoid modifications while iterating
            projectile.update(self.state, boundaries)

        self.state[player].score += reward

        if self.mode == "2p":
            # switch the turn
            self.turn = "enemy" if self.turn == "player" else "player"

        ##################### update done #####################

        return self.state, self.score(), self.done, {}

    def playout(self) -> dict[str, float]:
        # loop until the game is over
        while not self.terminal():
            moves = self.legalMoves()
            n = np.random.randint(0, len(moves) - 1)
            self.play(moves[n])  # random strategy
        return self.score()

    def board_matrix(self):
        # Create a matrix M of size max_x * max_y with a padding of 1 on each side
        rows = self.max_y + 2
        cols = self.max_x + 2
        M = np.ones((rows, cols, 3), dtype=np.uint8) * 240  # white background

        # fill the matrix with the elements of the environment

        ## fill with player
        M = fill_tank(self.state["player"], green, M)

        ## fill with enemies
        if self.mode == "2p":
            M = fill_tank(self.state["enemy"], red, M)
        for enemy in self.state["enemies"]:
            M = fill_tank(enemy, yellow, M)

        ## fill with obstacles
        # 3 x 3 square obstacle
        for obstacle in self.state["obstacles"]:
            M = fill_obstacle(obstacle, black, M)

        ## fill with projectiles
        for projectile in self.state["projectiles"]:
            M = fill_projectile(projectile, turquoise, red, M)

        return M

    def render(self, mode="human"):
        pygame.init()
        env = TankEnv()
        env.reset()

        game_main(self)
        pygame.quit()

    def print(self):
        M = self.board_matrix()
        plt.imshow(M)
        plt.axis("off")
        plt.show()


class Node:
    def __init__(self, board, parent=None, action=None):
        self.state = board  # copy.deepcopy(Board)
        self.parent = parent
        self.children = []
        self.visits = 0
        self.value = 0.0
        self.untried_actions = list(
            range(board.action_space.n)
        )  # assumes Discrete action space
        self.action = action

    def ucb_score(self, exploration_constant=1.41) -> float:
        if self.visits == 0:
            return float("inf")
        if self.parent is not None:
            return (self.value / self.visits) + exploration_constant * math.sqrt(
                math.log(self.parent.visits) / self.visits
            )
        else:
            return 0.0

    def is_fully_expanded(self) -> bool:
        return len(self.untried_actions) == 0

    def best_child(self, exploration_constant=1.41):
        return max(
            self.children, key=lambda child: child.ucb_score(exploration_constant)
        )
