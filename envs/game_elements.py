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
    
    def info(self):
        return (self.x, self.y, np.argmax(self.direction), self.label)
    
    def copy(self):
        direction_copy = self.direction.copy()
        return Tank(self.x, self.y, direction_copy, self.label)

    def update(self, action, occupied_positions, infos):
        # action: 0: up, 1: right, 2: down, 3: left, 4: stay, 5: shoot
        occupied_positions.remove((self.x, self.y))
        if not (action == 4 or action == 5):
            #if it matches, move forward
            if self.direction[action] == 1:
                x = self.x + self.direction[1] - self.direction[3] # right - left
                y = self.y + self.direction[2] - self.direction[0] # down - up
                if x < 0 or x >= infos['max_x'] or y < 0 or y >= infos['max_y']:
                    occupied_positions.add((self.x, self.y))
                    return
                # check collision with other tanks
                # check if the 9 squares are arround the tank are occupied
                boxes = [(x + i, y + j) for i in range(-2, 3) for j in range(-2, 3)]
                if any(box in occupied_positions for box in boxes):
                    occupied_positions.add((self.x, self.y))
                    return
                self.x = x
                self.y = y

            #if it doesn't, rotate
            else:
                self.direction = [0,0,0,0]
                self.direction[action] = 1

        occupied_positions.add((self.x, self.y))

        # TODO: resolve the shoot method
    
    def update_strategic(self, occupied_positions, infos, strategy=0):
        if strategy == 0:
            # random strategy
            action = np.random.randint(0, 5) # TODO: change 5 to 6 after
            self.update(action, occupied_positions, infos)
        
        if strategy == 1:
            # follow more its direction with a probability of prob
            prob = 0.7
            if np.random.rand() < prob:
                action = np.argmax(self.direction)
                self.update(action, occupied_positions, infos)
            else:
                return self.update_strategic(occupied_positions, infos, strategy=0)

        if strategy == 2:
            # go to the player with a probability of prob
            prob = 0.1
            if np.random.rand() < prob:
                # go to the player
                if self.x < infos['player_position'][0]:
                    action = 1
                elif self.x > infos['player_position'][0]:
                    action = 3
                elif self.y < infos['player_position'][1]:
                    action = 2
                elif self.y > infos['player_position'][1]:
                    action = 0
                else:
                    action = 4
                self.update(action, occupied_positions, infos)
            else:
                return self.update_strategic(occupied_positions, infos, strategy=1)
            

    def shoot(self, state):
        # create a new projectile
        # to be called after the updating of the projectiles
        p = Projectile(
            self.x + self.direction[2] - self.direction[3],
            self.y + self.direction[0] - self.direction[1],
            self.direction,
            state,
        )
        # TODO :add it to the set of projectiles

class Projectile:
    def __init__(self, x, y, direction,label=1):
        # size = 1 px
        self.x = x
        self.y = y
        self.direction = direction
        self.label = label

        self.info = (self.x, self.y, np.argmax(self.direction), self.label)

    def update(self, state):
        # move the projectile
        # need global variables for the boundaries

        # move
        self.x += self.direction[2] - self.direction[3]
        self.y += self.direction[0] - self.direction[1]

        # check boundaries
        if self.x < 0 or self.x > max_x or self.y < 0 or self.y > max_y:
            TODO = "remove the projectile from the set"

        # check annulation
        for projectile in projectiles:  # set, probably state.projectiles
            if projectile.x == self.x and projectile.y == self.y:
                TODO = "remove both projectiles from the set"

        # checking the collision with the tanks is gonna be somewhere else
                
    def not_colliding_with(self, object):
        # if object is a tank
        if isinstance(object, Tank):
            min_distance = 2
        # if object is a projectile
        if isinstance(object, Projectile):
            min_distance = 1
        return abs(self.x - object.x) >= min_distance or abs(self.y - object.y) >= min_distance


class Obstacle:
    # in case we wanna complicate the game
    def __init__(self, x, y):
        self.x = x
        self.y = y
        # squares to be combined
