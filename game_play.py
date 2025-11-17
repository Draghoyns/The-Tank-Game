import pygame
import numpy as np

from envs import *
from utils.coloring import green, red


def main(env):

    # Set up the display
    screen_size = (env.max_x * 20, env.max_y * 20)  # Scale up the game screen
    screen = pygame.display.set_mode(screen_size)
    clock = pygame.time.Clock()
    font = pygame.font.Font(None, 36)

    running = True
    while running:
        # Check for events
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False

        keys = pygame.key.get_pressed()
        action = 4  # Default action (stay)

        key_to_action = {
            pygame.K_LEFT: 0,
            pygame.K_DOWN: 1,
            pygame.K_RIGHT: 2,
            pygame.K_UP: 3,
            pygame.K_SPACE: 5,  # Shoot
        }

        for key, act in key_to_action.items():
            if keys[key]:
                action = act
                break

        # Update the environment
        state, reward, done, trunc, _ = env.step(action)
        if done or trunc:
            # running = False
            env.reset()

        # Render the game state
        frame = env.render()
        frame = np.repeat(
            np.repeat(frame, 18, axis=0), 18, axis=1
        )  # Scale up the frame for visibility
        surface = pygame.surfarray.make_surface(frame)
        screen.blit(surface, (0, 0))

        # display score
        value = int(state["player"].score)
        score = f"Score: {value}"
        if value >= 0:
            score_surface = font.render(score, True, green)
        else:
            score_surface = font.render(score, True, red)
        score_width = score_surface.get_width()  # Get the width of the rendered text
        screen.blit(
            score_surface, (screen.get_width() - score_width - 10, 10)
        )  # Position at top-right with 10px padding

        pygame.display.flip()

        # Cap the frame rate
        clock.tick(9)


if __name__ == "__main__":
    # Initialize pygame and the environment
    pygame.init()
    env = TankEnv(obstacles="")
    env.reset()

    # Run the game
    main(env)

    pygame.quit()
