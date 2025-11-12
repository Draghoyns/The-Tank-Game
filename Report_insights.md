# On the report

- redundancy in introduction ? 
- determining the observation in itself is a great aspect of the project

- DQN : look at the different stages of DQN (see lab6, then dper by deepmind)

    Horgan, Dan, John Quan, David Budden, Gabriel Barth-Maron, Matteo Hessel, Hado van Hasselt, and David Silver.
     [‘Distributed Prioritized Experience Replay’. 2 March 2018](https://doi.org/10.48550/arXiv.1803.00933)
- integrate literature
- if talk about the Java game, tell how it influences our work

- look at similar environment : [atari](https://paperswithcode.com/sota/atari-games-on-atari-2600-asteroids)

- do not redefine $Q$-table and $\varepsilon$-greedy strategy
- Manhattan distance formula
- formal definition and formulas of $Q$-table and $\varepsilon$-greedy strategy
- detail the theoretical framework to develop the agent
- pseudo code / algorithms of how we used $Q$-table and $\varepsilon$-greedy

- discussion : random agent doesnt rely on observartion space so it has no influence whatsoever
- discussion on challenges faced by agents in the complex environment (what failed, what had to be changed)

- details on the experimental part : number of iterations, measures, hyperparameters
- evaluation methods to test environment's adequacy : description, data, visuals

# On the code and implementation

- study the reward function : is penalizing inaction necessary ?
- use visual representation more wisely in the code
- compare behaviors when constraints : red zone on the map, different levels, additional variables to influence decision-making => adaptability of the agent