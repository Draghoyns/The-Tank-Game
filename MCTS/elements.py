import numpy as np

from envs.game_elements import Tank


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


class Board(object):
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

        # game settings
        self.total_ennemies_to_kill = total_ennemies_to_kill
        self.initial_ennemies = 2
        self.probability_new_enemy = 0.01
        self.obstacles = obstacles

        # 2p setting
        self.turn = "player"  # player or enemy

        # score settings
        self.reward_enemy_killed = 1
        self.reward_player_dead = -10
        self.reward_used_projectile = -0.1
        self.reward_nothing = -0.1
        self.timestep = -0.01

        # assertions
        assert max_x > 0
        assert max_y > 0
        assert max_enemies_on_screen > 0
        assert max_enemies_on_screen <= total_ennemies_to_kill
        assert (max_enemies_on_screen + 1) * 9 * 2 <= max_x * max_y

        # initialization

        self.state = {
            "player": set(),
            "enemies": set(),  # (Tank(0, 0, np.array([0, 0, 1, 0])), Tank(0, 0, np.array([0, 0, 1, 0])), ...)
            "projectiles": set(),  # (Projectile(0, 0, np.array([0, 0, 1, 0]), label=0), Projectile(0, 0, np.array([0, 0, 1, 0]), label=1), ...)
            "obstacles": set(),
            "enemy":set()
        }
        self.occupied_positions = set()

        self.done = False
        self.info = {}

    def reset(self):
        self.occupied_positions = set()
        self.done = False

        # __________PLAYER__________#
        # place the player randomly
        x = np.random.randint(0, self.max_x)
        y = np.random.randint(0, self.max_y)

        direction = np.zeros(4, dtype=int)
        direction[np.random.randint(0, 4)] = 1  # random direction

        player = Tank(x, y, direction, label=0)
        self.state["player"] = player

        self.occupied_positions.add((x, y))

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
            self.max_enemies_on_screen = 1
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
        self.state["enemy"] = enemies.pop()

        # __________COHERENCE__________#
        # if the player is stuck, we reset
        # stuck = more than 3 obstacles around the player
        boxes = self.state["player"].big_bounding_box()
        obstacles_around_player = [box for box in boxes if box in obstacles]
        if len(obstacles_around_player) > 3:
            print("#### player is stuck, resetting ####")
            self.reset()
        else:
            print("#### environnement reset successfully ####")

    def legalMoves(self):
        # set of possible moves
        # list of Move objects
        moves = []
        for action in range(6):
            # check if the move is valid
            x, y, direction, label = self.state[self.turn].info()
            dir = [0, 0, 0, 0]
            dir[direction] = 1
            move = Move(label, direction, action, x, y)
            if move.valid(self):
                moves.append(move)

        return moves

    def score(self) -> float:
        # current score of the player
        if self.mode == "1p":
            return self.state["player"].score # to be sure but normally self.turn doesn't change in 1p mode
        else:
            return {"p1": self.state["player"].score, "p2": self.state["enemy"].score}

    def terminal(self) -> bool:
        # check if the game is over
        # if the player is dead, the game is over
        # if the player has killed all the enemies, the game is over

        return self.done

    def play(self, move):
        # play the move on the board
        action = move.action
        player = self.state[self.turn] # Tank object
        eni = self.state["enemy"] if self.turn == "player" else self.state["player"]

        reward = self.timestep

        ## canceling projectiles that touch each other if necessary
        # in theory it works, in practive there is some bug
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
        ## reward_enemy_killed for each defeated enemy
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
        if self.mode == "1p":    
            for enemy in list(self.state["enemies"]):
                enemy_boxes = enemy.bounding_box()
                for projectile in list(self.state["projectiles"]):

                    if (
                        projectile.x,
                        projectile.y,
                    ) in enemy_boxes and projectile.label == 0:
                        self.state["enemies"].remove(enemy)
                        self.occupied_positions.remove((enemy.x, enemy.y))
                        self.state["projectiles"].remove(projectile)
                        reward += self.reward_enemy_killed
                        break

        else:
            enemy_boxes = eni.bounding_box()
            for projectile in list(self.state["projectiles"]):
                if (
                    projectile.x,
                    projectile.y,
                ) in enemy_boxes and projectile.label == player.label:
                    self.state["projectiles"].remove(projectile)
                    reward += self.reward_enemy_killed
                    break 

        # Check if the player is dead
        ## if the player is dead: done = True, reward = reward_player_dead
        ## if the player is not dead: done = False
        boxes = player.bounding_box()
        ennemies_projectiles_positions = [
            (projectile.x, projectile.y)
            for projectile in self.state["projectiles"]
            if projectile.label == eni.label
        ]
        if any(pos in boxes for pos in ennemies_projectiles_positions):
            self.done = True
            reward += self.reward_player_dead

        ##################### update #####################

        # Update the player's state
        ## strategy: based on the action
        ## reward if the action is "stay" or "shoot", 0 otherwise
        boundaries = {
            "max_x": self.max_x,
            "max_y": self.max_y,
        }
        player.update(
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

        player.score += reward

        if self.mode == "2p":
            # switch the turn
            self.turn = "enemies" if self.turn == "player" else "player"

        ##################### update done #####################


    def playout(self):
        # loop until the game is over
        while (not self.terminal()):
            moves = self.legalMoves ()
            n = np.random.randint (0, len (moves) - 1)
            self.play (moves [n]) # random strategy
        return self.score ()

    def render(self):

        # careful : not render enemies if playing 2p
        # not render enemy if playing 1p
        pass
