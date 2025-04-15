## Game description
The Tank Game is a simple game that comes from the same series as Tetris.
The user plays a tank, which has to shoot other enemy tanks while avoiding their projectiles.
The goal is to kill a certain amount of enemies while achieving the highest possible score.

## Contributions

The game was fully implemented from scratch, with all the necessary dynamics. On top of that, the environment and the classes were adapted to suit to the Monte Carlo Search course and apply the different relevant algorithms.

The game itself is simple, but in terms of computation and size of the action space, it might be not so simple for the studies in this course.

Different game dynamics were tested in order to study the algorithms.

The game is originally a 1-player game, 
with computer agents acting as enemies (several of them, spawning during the game). The objective being studying the performance of algorithms against it other, a 2-player game was designed.
The first design of this 2-player game was a PvP (player vs player), with a win being a single kill.

This design was tested on a simple competition, Flat Monte Carlo vs UCT. However, even a single game was too slow to have a result.

The design was therefore changed to the tank game with 3 entities : player 1, player 2, and a third enemy agent, that is hostile to both players. This enemy plays a random strategy, but moves twice as fast as the players (because players take turn when playing)


## Experiments

A first competition was run, for a number of simulations equal to $10$ for each algorithm and a varying number of total games on which to average. The result is as follows :


| UCT  | FlatMC | number of games |
| ---- | ------ | :-------------: |
| -3.1 | 5      |       10        |
| 3.94 | -1.4   |       50        |
| 2.04 | 0.8    |       75        |
| 1.91 | -2.21  |       100       |

The results were not that good, because the number of simulations down the tree is too small. We can still see that UCT tends to perform better than Flat MC.
For $n_{sim}=100$:

| UCT | FlatMC | number of games |
| --- | ------ | :-------------: |
| 0.9 | 2      |       10        |
| 3.3 | -2.6   |       50        |
|  3.85   |   -1.21     |       75        |
|     |        |       100       |

## Limitations
This study obviously has its limitations.
The game space may be difficult to handle by algorithms, but the dynamics are very simple. Even more so that a single game ends at the first kill all entities considered.
However, we clearly see the application of the algorithms, some of them performing better than the others.