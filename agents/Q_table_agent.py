import numpy as np
import math


class QTable:
    def __init__(
        self, num_distances_manhattan, action_space_size, num_orientations_kronecker=2
    ):
        self.state_space_dimension_a = num_distances_manhattan
        self.state_space_dimension_b = num_orientations_kronecker
        self.action_space_size = action_space_size
        self.q_table = np.zeros(
            (num_distances_manhattan, num_orientations_kronecker, action_space_size)
        )

    def get_q_value(self, distance, orientation, action):
        return self.q_table[distance, orientation, action]

    def set_q_table(self, q_table):
        self.q_table = q_table

    def set_q_value(self, distance, orientation, action, value):
        self.q_table[distance, orientation, action] = value

    def choose_action(self, distance, orientation, epsilon):
        if np.random.rand() < epsilon:
            # Explore: choose a random action
            return np.random.choice(self.action_space_size)
        else:
            # Exploit: choose the action with the highest Q-value
            return np.argmax(self.q_table[distance, orientation])

    def update_q_value(
        self,
        distance,
        orientation,
        action,
        learning_rate,
        reward,
        discount_factor,
        next_distance,
        next_orientation,
    ):
        current_q_value = self.get_q_value(distance, orientation, action)
        max_future_q_value = np.max(self.q_table[next_distance, next_orientation])
        new_q_value = current_q_value + learning_rate * (
            reward + discount_factor * max_future_q_value - current_q_value
        )
        self.set_q_value(distance, orientation, action, new_q_value)


def manhattan_distance(x1, y1, x2, y2):
    return abs(x1 - x2) + abs(y1 - y2)


def get_vector_normalized(x1, y1, x2, y2):
    """
    Calculates and normalizes the direction vector between points (x1, y1) and (x2, y2).
    """
    dx = x2 - x1
    dy = y2 - y1
    norm = math.sqrt(dx**2 + dy**2)

    if norm == 0:
        return (0, 0)
    norm_vector = (dx / norm, dy / norm)
    return norm_vector


def scalar_product(vector1, vector2):
    if len(vector1) != len(vector2):
        raise ValueError("Vectors must have the same dimension")
    product = sum(x * y for x, y in zip(vector1, vector2))

    return product


def grab_distance_and_kronecker(
    state,
):  # takes state as decribed in tan_env.py and returns distance between player and closest enemy
    tank_player = state["player"]
    x_player, y_player, direction_player, _ = tank_player.info()
    list_enemies = list(state["enemies"])

    if len(list_enemies) == 0:
        return 0, 0

    closest_enemy = list_enemies[0]
    x_enemy, y_enemy, _, _ = closest_enemy.info()
    d_min = manhattan_distance(x_player, x_enemy, y_player, y_enemy)

    for enemy in list_enemies:
        x_enemy, y_enemy, _, _ = enemy.info()
        if manhattan_distance(x_player, x_enemy, y_player, y_enemy) < d_min:
            d_min = manhattan_distance(x_player, x_enemy, y_player, y_enemy)
            closest_enemy = enemy

    x_enemy, y_enemy, _, _ = closest_enemy.info()
    box = [(x_enemy + i, y_enemy + j) for i in range(-2, 3) for j in range(-2, 3)]

    direction_orientation_map = {0: (0, 1), 1: (1, 0), 2: (0, -1), 3: (-1, 0)}
    key = int(np.argmax(direction_player))
    orientation_vector = direction_orientation_map.get(key)

    list_scalar_product = [0]
    for pos_x, pos_y in box:
        direction_vector = get_vector_normalized(
            x_player, y_player, pos_x, pos_y
        )  # calculate director vector to get direction player_enemy for each pixel of enemy
        list_scalar_product.append(scalar_product(orientation_vector, direction_vector))

    kronecker = 0
    if 1 in list_scalar_product:
        kronecker = 1
    return d_min, kronecker
