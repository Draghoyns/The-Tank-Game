import numpy as np
from enum import Enum
from envs.game_elements import Tank, Projectile


class Color(Enum):
    player = [92, 184, 92]  # green
    enemy = [240, 173, 78]  # yellow
    obstacle = [0, 0, 0]  # black

    player_projectile = [64, 224, 208]  # turquoise
    enemy_projectile = [217, 100, 79]  # red

    positive_score = [92, 184, 92]  # green
    negative_score = [217, 100, 79]  # red


def fill_tank(tank: Tank, color_code: Color, game_board: np.ndarray) -> np.ndarray:
    x_coord, y_coord, direction, _ = tank.info()
    x_coord += 1  # because of the padding
    y_coord += 1  # because of the padding

    color = color_code.value

    game_board[y_coord, x_coord] = color

    if direction in [1, 2]:
        game_board[y_coord - 1, x_coord - 1, :] = color
    if direction in [0, 1, 3]:
        game_board[y_coord - 1, x_coord, :] = color
    if direction in [2, 3]:
        game_board[y_coord - 1, x_coord + 1, :] = color
    if direction in [0, 2, 3]:
        game_board[y_coord, x_coord - 1, :] = color
    if direction in [0, 1, 2]:
        game_board[y_coord, x_coord + 1, :] = color
    if direction in [0, 1]:
        game_board[y_coord + 1, x_coord - 1, :] = color
    if direction in [1, 2, 3]:
        game_board[y_coord + 1, x_coord, :] = color
    if direction in [0, 3]:
        game_board[y_coord + 1, x_coord + 1, :] = color
    return game_board


def fill_obstacle(
    obstacle: tuple[int, int], color: Color, gameboard: np.ndarray
) -> np.ndarray:
    x_coord, y_coord = obstacle
    x_coord += 1
    y_coord += 1
    for y_increment in range(-1, 2):
        for x_increment in range(-1, 2):
            gameboard[y_coord + y_increment, x_coord + x_increment, :] = color.value
    return gameboard


def fill_projectile(projectile: Projectile, gameboard: np.ndarray) -> np.ndarray:
    x_coord, y_coord, _, label = projectile.info()
    x_coord += 1
    y_coord += 1

    map_label_color = {0: Color.player_projectile, 1: Color.enemy_projectile}

    gameboard[y_coord, x_coord, :] = map_label_color[label]
    return gameboard
