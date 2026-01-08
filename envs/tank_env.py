import gymnasium as gym
from gymnasium import spaces
import matplotlib.pyplot as plt
import numpy as np

from envs.game_elements import *
from utils.coloring import (
    fill_tank,
    fill_obstacle,
    fill_projectile,
    Color,
)


# Creating environnement


class TankEnv(gym.Env):
    """2D tank environment for single-player or two-player modes.

    Args:
        max_x (int): Width of the game screen.
        max_y (int): Height of the game screen.
        max_enemies_on_screen (int): Maximum simultaneous enemies.
        total_enemies_to_kill (int): Number of kills required to finish the game.
        obstacles (str): One of {"", "low", "high"} describing obstacle density ("" for no obstacle).
        mode (str): "1p" for single-player or "2p" for PvP for algorithmic testing.
    """

    metadata = {"render.modes": ["human"]}

    def __init__(
        self,
        max_x: int = 20,
        max_y: int = 20,
        max_enemies_on_screen: int = 5,
        total_ennemies_to_kill: int = 10,
        obstacles: str = "",
        mode: str = "1p",
    ):
        super(TankEnv, self).__init__()

        self.max_x = max_x  # Width of grid
        self.max_y = max_y  # Height of grid
        self.max_enemies_on_screen = max_enemies_on_screen
        self.max_projectiles = max_x * max_y

        self.total_ennemies_to_kill = total_ennemies_to_kill
        self.initial_ennemies = 2
        self.obstacles = obstacles
        self.mode = mode

        # sanity checks
        assert max_x > 0
        assert max_y > 0
        assert max_enemies_on_screen > 0
        assert max_enemies_on_screen <= total_ennemies_to_kill
        assert (max_enemies_on_screen + 1) * 9 * 2 <= max_x * max_y

        self.action_space = spaces.Discrete(
            6
        )  # 0: up, 1: right, 2: down, 3: left, 4: stay, 5: shoot

        dtypes = np.int32
        self.observation_space = spaces.Dict(
            {
                "player": spaces.Box(
                    low=np.array([0, 0, 0]),
                    high=np.array([self.max_x, self.max_y, 4]),
                    dtype=dtypes,
                ),  # x, y, direction
                "enemies": spaces.Box(
                    low=np.zeros((self.max_enemies_on_screen, 3), dtype=dtypes),
                    high=np.array(
                        [self.max_x, self.max_y, 4] * self.max_enemies_on_screen
                    ).reshape(self.max_enemies_on_screen, 3),
                    dtype=dtypes,
                ),
                "projectiles": spaces.Box(
                    low=np.zeros((self.max_projectiles, 4), dtype=dtypes),
                    high=np.array(
                        [self.max_x, self.max_y, 4, 1] * self.max_projectiles
                    ).reshape(self.max_projectiles, 4),
                    dtype=dtypes,
                ),  # x, y, direction, from (0: player, 1: enemy)
                "obstacles": spaces.Box(
                    low=np.zeros((self.max_x, self.max_y), dtype=dtypes),
                    high=np.ones((self.max_x, self.max_y), dtype=dtypes),
                    dtype=dtypes,
                ),  # obstacles
            }
        )
        self.action_space = spaces.Discrete(6)

        self.state = {
            "player": Tank(0, 0, np.array([0, 0, 1, 0]), label=0),
            "enemies": set(),  # Tank objects
            "projectiles": set(),  # Projectile objects, could be an array the size of the game screen ?
            "obstacles": set(),
        }

        # Set of all positions occupied by tanks
        self.occupied_positions = set()

        self.probability_new_enemy = 0.01

        # Rewards
        ## kill-based reward
        self.reward_enemy_killed = 10
        self.reward_player_dead = -20

        ## action-based reward
        self.reward_used_projectile = -0.1
        self.reward_nothing = -0.01

        ## time-based reward
        self.timestep = -0.001

        # for accumulating reward
        self.reward = 0

        self.done = False  # terminated ?
        self.info = {}

    def reset(
        self,
        *,
        initial_run: bool = True,
        seed: int | None = None,
        options: dict | None = None
    ) -> tuple:
        super().reset(seed=seed)
        self.occupied_positions = set()  # "board"
        self.done = False

        if initial_run:

            # place the player
            ## strategy : random
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

            # place obstacles
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

        # place enemies, beware of collisions
        ## strat: self.initial_ennemies random ennemies
        ennemies = set()
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

                ennemies.add(enemy)
                self.occupied_positions.add((x, y))
                placed = True

        self.state["enemies"] = ennemies

        # if the player is stuck, we reset
        # stuck = more than 3 obstacles around the player
        boxes = self.state["player"].big_bounding_box()
        obstacles_around_player = [box for box in boxes if box in obstacles]
        if len(obstacles_around_player) > 3:
            print("#### player is stuck, resetting ####")
            self.reset()
        else:
            print("#### environnement reset successfully ####")
        return (self.state, {})

    def clean(self, action: int) -> None:
        """Cleans the game board from killed enemies and used projectiles.
        Args:
            action (int): next action to perform
        """
        ## canceling projectiles that touch each other if necessary
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

        # Clean up defeated enemies and used projectiles
        ## reward_enemy_killed for each defeated enemy
        reward = 0
        obstacle_boxes = []
        for obstacle in list(self.state["obstacles"]):
            boxes = [
                (obstacle[0] + i, obstacle[1] + j)
                for i in range(-1, 2)
                for j in range(-1, 2)
            ]
            obstacle_boxes += boxes

        for enemy in list(self.state["enemies"]):
            enemy_boxes = enemy.bounding_box()
            for projectile in list(self.state["projectiles"]):

                if (projectile.x, projectile.y) in obstacle_boxes:
                    self.state["projectiles"].remove(projectile)

                if (
                    projectile.x,
                    projectile.y,
                ) in enemy_boxes and projectile.label == 0:
                    self.state["enemies"].remove(enemy)
                    self.occupied_positions.remove((enemy.x, enemy.y))
                    self.state["projectiles"].remove(projectile)
                    reward += self.reward_enemy_killed
                    self.state["player"].kills += 1
                    break
        self.state["player"].score += reward

    def check_death(self, *, who: str) -> None:
        """Checks if the called tank is dead. If yes, the game is marked as done.
        If the player is dead, penalty is applied.

        TODO : refactor to respect Single Responsibility Principle
        """
        reward = 0
        label_map = {"player": 0, "enemy": 1}

        boxes = self.state[who].bounding_box()
        ennemies_projectiles_positions = []
        for projectile in list(self.state["projectiles"]):
            if projectile.label != label_map[who]:  # not their projectile
                ennemies_projectiles_positions.append(projectile)

        for projectile in ennemies_projectiles_positions:
            if (projectile.x, projectile.y) in boxes:
                self.state["projectiles"].remove(projectile)
                if who == "player":
                    reward += self.reward_player_dead
                self.state[who].deaths += 1
                self.done = True
                # self.reset(initial_run=False)
        self.state["player"].score += reward

    def step(self, action: int) -> tuple[dict, float, bool, bool, dict]:
        reward = self.timestep

        self.clean(action)

        # Add 1 enemy if the number of active enemies is less than max_enemies
        ## strategy: randomly with a probability of self.probability_new_enemy
        if (
            len(self.state["enemies"]) < self.max_enemies_on_screen
            and np.random.rand() < self.probability_new_enemy
        ) or len(self.state["enemies"]) == 0:
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

                self.state["enemies"].add(enemy)
                self.occupied_positions.add((x, y))
                placed = True

        # Check if the player is dead
        # the game doesn't end when the player dies
        self.check_death(who="player")

        # for 2p game, check if enemy is dead
        if self.mode == "2p":
            self.check_death(who="enemy")

        # the game doesn't end when the player dies
        if self.state["player"].kills >= self.total_ennemies_to_kill:
            self.done = True

        ##################### update #####################

        # Update the player's state
        ## strategy: based on the action
        ## reward if the action is "stay" or "shoot", 0 otherwise
        boundaries = {
            "max_x": self.max_x,
            "max_y": self.max_y,
        }
        self.state["player"].update(
            action, self.state, self.occupied_positions, boundaries
        )
        if action == 4:
            reward += self.reward_nothing
        elif action == 5:
            reward += self.reward_used_projectile

        # Update the state of enemies
        ## strategy: random
        for enemy in self.state["enemies"]:
            enemy.update_strategic(
                self.state, self.occupied_positions, boundaries, strategy=2
            )

        # Update the state of projectiles
        ## position
        for projectile in list(
            self.state["projectiles"]
        ):  # list() to avoid modifications while iterating
            projectile.update(self.state, boundaries)

        ##################### update done #####################

        self.state["player"].score += reward
        truncated = False  # to be re-considered

        return (self.state, reward, self.done, truncated, self.info)

    # __________RENDERING__________#

    def render(self, mode="human") -> np.ndarray:
        # Create a matrix M of size max_x * max_y with a padding of 1 on each side
        rows = self.max_y + 2
        cols = self.max_x + 2
        M = np.ones((rows, cols, 3), dtype=np.uint8) * 240  # white background

        # fill the matrix with the elements of the environment
        ## fill with player
        M = fill_tank(self.state["player"], Color.player, M)

        ## fill with enemies
        for enemy in self.state["enemies"]:
            M = fill_tank(enemy, Color.enemy, M)

        ## fill with obstacles
        # 3 x 3 square obstacle
        for obstacle in self.state["obstacles"]:
            M = fill_obstacle(obstacle, Color.obstacle, M)

        ## fill with projectiles
        for projectile in self.state["projectiles"]:
            M = fill_projectile(projectile, M)

        # return frame
        return M

    def plot_render(self) -> None:
        """Generates the rendered frame and plots it."""
        gameboard = self.render()
        plt.axis("off")
        plt.imshow(gameboard)
        plt.show()
