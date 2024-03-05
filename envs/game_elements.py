class Tank:
    def __init__(self, x, y, direction, label=0):
        """
        Initialise un tank.
        x, y: position du tank
        direction: direction du tank
        label: 0 si le tank est un ennemi, 1 si c'est le joueur
        """
        self.x = x
        self.y = y
        self.direction = direction
        self.label = label

    def move(self, action, state):
        pass

    def shoot(self):
        pass

class Projectile:
    def __init__(self, x, y, direction, state):
        self.x = x
        self.y = y
        self.direction = direction

    def update(self):
        pass