def fill_tank(tank, color, M):
    x, y, dir, _ = tank.info()
    x += 1  # because of the padding
    y += 1  # because of the padding

    M[y, x] = color
    if dir in [1, 2]:
        M[y - 1, x - 1, :] = color
    if dir in [0, 1, 3]:
        M[y - 1, x, :] = color
    if dir in [2, 3]:
        M[y - 1, x + 1, :] = color
    if dir in [0, 2, 3]:
        M[y, x - 1, :] = color
    if dir in [0, 1, 2]:
        M[y, x + 1, :] = color
    if dir in [0, 1]:
        M[y + 1, x - 1, :] = color
    if dir in [1, 2, 3]:
        M[y + 1, x, :] = color
    if dir in [0, 3]:
        M[y + 1, x + 1, :] = color
    return M


def fill_obstacle(obstacle, color, M):
    x, y = obstacle
    x += 1
    y += 1
    for i in range(-1, 2):
        for j in range(-1, 2):
            M[y + i, x + j, :] = color
    return M


def fill_projectile(projectile, color_0, color_1, M):
    x, y, _, label = projectile.info()
    x += 1
    y += 1
    if label == 0:
        M[y, x, :] = color_0
    else:
        M[y, x, :] = color_1
    return M
