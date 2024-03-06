class Tank:
    def __init__(self, x, y, direction, state, label=1):
        # defined by the center (a tank = 3x3 in display)
        self.x = x
        self.y = y
        self.direction = direction
        self.label = label
        self.label = label

    def move(self, action):
        # matching action and direction
        if not (action == 4 or action == 5):
            #if it matches, move forward
            if self.direction[action] == 1:
                self.x += self.direction[2] - self.direction[3]
                self.y += self.direction[0] - self.direction[1]
            #if it doesn't, rotate
            else:
                self.direction = [0,0,0,0]
                self.direction[action] = 1

    def shoot(self, state):
        # create a new projectile
        # to be called after the updating of the projectiles
        p = Projectile(
            self.x + self.direction[2] - self.direction[3],
            self.y + self.direction[0] - self.direction[1],
            self.direction,
            state,
        )
        #TODO :add it to the set of projectiles


class Projectile:
    def __init__(self, x, y, direction, state,label=1):
        # size = 1 px
        self.x = x
        self.y = y
        self.direction = direction
        self.label = label

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


class Obstacle:
    # in case we wanna complicate the game
    def __init__(self, x, y):
        self.x = x
        self.y = y
        # squares to be combined
