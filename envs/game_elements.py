import numpy as np


class Tank:
    def __init__(self, x, y, direction, label=1):
        # defined by the center (a tank = 3x3 in display)
        # Direction: 0 = up, 1 = right, 2 = down, 3 = left
        # label: 0 = player, 1 = enemy
        self.x = x
        self.y = y
        self.direction = direction
        self.label = label
        self.score = 0
        self.kills = 0
        self.deaths = 0

    def bounding_box(self):
        return [
            (self.x + i, self.y + j)
            for i in range(-1, 2)
            for j in range(-1, 2)
        ]
    def big_bounding_box(self):
        return [
            (self.x + i, self.y + j)
            for i in range(-2, 3)
            for j in range(-2, 3)
        ]


    def info(self):
        return (self.x, self.y, np.argmax(self.direction), self.label)

    def copy(self):
        direction_copy = self.direction.copy()
        return Tank(self.x, self.y, direction_copy, self.label)

    def update(self, action, state, occupied_positions, boundaries):
        # action: 0: up, 1: right, 2: down, 3: left, 4: stay, 5: shoot

        if not (action == 4 or action == 5):
            # if it matches, move forward
            if self.direction[action] == 1:
                occupied_positions.remove((self.x, self.y))
                x = self.x + self.direction[1] - self.direction[3]  # right - left
                y = self.y + self.direction[2] - self.direction[0]  # down - up
                if x < 0 or x >= boundaries["max_x"] or y < 0 or y >= boundaries["max_y"]:
                    occupied_positions.add((self.x, self.y))
                    return occupied_positions
                # check collision with other tanks
                # check if the 9 squares are arround the tank are occupied
                boxes = [(x + i, y + j) for i in range(-2, 3) for j in range(-2, 3)]
                if any(box in occupied_positions for box in boxes):
                    occupied_positions.add((self.x, self.y))
                    return occupied_positions
                self.x = x
                self.y = y
                occupied_positions.add((self.x, self.y))

            # if it doesn't, rotate
            else:
                self.direction = [0, 0, 0, 0]
                self.direction[action] = 1

        if action == 5:
            self.shoot(state)

        return occupied_positions

    def update_strategic(self, state, occupied_positions, boundaries, strategy=0):
        if strategy == 0:
            # random strategy
            action = np.random.randint(0, 6)  # TODO: change 5 to 6 after
            occupied_positions = self.update(action, state, occupied_positions, boundaries)

        if strategy == 1:
            # follow more its direction with a probability of prob
            prob = 0.7
            if np.random.rand() < prob:
                action = np.argmax(self.direction)
                occupied_positions = self.update(action, state, occupied_positions, boundaries)
            else:
                return self.update_strategic(
                    state, occupied_positions, boundaries, strategy=0
                )

        if strategy == 2:
            # go to the player with a probability of prob
            prob = 0.1
            if np.random.rand() < prob:
                # go to the player
                if self.x < state["player"].x:
                    action = 1
                elif self.x > state["player"].x:
                    action = 3
                elif self.y < state["player"].y:
                    action = 2
                elif self.y > state["player"].y:
                    action = 0
                else:
                    action = 4
                occupied_positions = self.update(action, state, occupied_positions, boundaries)
            else:
                return self.update_strategic(
                    state, occupied_positions, boundaries, strategy=1
                )
        
        return occupied_positions

    def shoot(self, state):
        # create a new projectile
        # to be called after the updating of the projectiles
        p = Projectile(
            self.x + 2 * (self.direction[1] - self.direction[3]),
            self.y + 2 * (self.direction[2] - self.direction[0]),
            self.direction,
            label=self.label,
        )
        state["projectiles"].add(p)


class Projectile:
    def __init__(self, x, y, direction, label):
        self.x = x
        self.y = y
        self.direction = direction
        self.label = label

    def info(self):
        return (self.x, self.y, np.argmax(self.direction), self.label)

    def update(self, state, boundaries):
        # move
        self.x += self.direction[1] - self.direction[3]  # right - left
        self.y += self.direction[2] - self.direction[0]  # down - up

        # check if it's out of bondaries
        if (
            self.x <= -1
            or self.x > boundaries["max_x"]
            or self.y <= -1
            or self.y > boundaries["max_y"]
        ):  # add + or - 1 because of padding
            state["projectiles"].remove(self)
