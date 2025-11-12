# The Tank Game

The Tank Game is a simple game that comes from the same series as Tetris.
The user plays a tank, which has to shoot other enemy tanks while avoiding their projectiles.
The goal is to kill a certain amount of enemies while achieving the highest possible score.

The Tank Game itself is already coded in Java (**TODO : add link**),
but as we want to apply methods to solve / optimize the plays,
Python was more suitable for us so we re-implemented the game (which was not the difficult bit).

## Content of the project

The project is far from being done at this stage.

The game exists, and is playable.

This is an academic project.
Nothing really relevant except the Python "implementation" of the game.

We need to implement all kinds of methods, RL and Monte Carlo Search,
to experiment with them on this particular game.

## Contributions

The game was fully implemented from scratch, with all the necessary dynamics.

Different game dynamics were tested in order to study the algorithms.

The game is originally a 1-player game, 
with computer agents acting as enemies (several of them, spawning during the game). The objective being studying the performance of algorithms against each other, a 2-player game was designed.

The first design of this 2-player game was a PvP (player vs player), with a win being a single kill.

Then the design was changed to the tank game with 3 entities : player 1, player 2, and a third enemy agent, that is hostile to both players. This enemy plays a random strategy, but moves twice as fast as the players (because players take turn when playing, and the enemy moves once after each player's turn).

## Playing

Install the requirements.

Run `game_play.py`.

A window will pop up, with a green tank and yellow tanks. You are the green player.

You can move with arrow keys (up - down - left - right) and shoot with the space bar.

If you die, the game resets. You cannot end the game unless you quit.

TODO :
- show the play time
- stop if the player dies
- make a fill function in game elements to be called when rendering 
- refactor parts of the code that is redundant

## Limitations
This study obviously has its limitations.
The game space may be difficult to handle by algorithms, but the dynamics are very simple.
Even more so that a single game ends at the first kill all entities considered.
