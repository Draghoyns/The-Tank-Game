import copy
import math
import random

from MCTS.utils import deepcopy_board
from MCTS.elements import Node


class FlatMC:
    def __init__(self, board, player, num_simulations=1000):
        self.board = board
        self.num_simulations = num_simulations
        self.player = player

    def algo(self):
        moves = self.board.legalMoves()
        bestScore = 0
        bestMove = 0
        for m in range(len(moves)):
            sum = 0
            for _ in range(self.num_simulations // len(moves)):
                b = copy.deepcopy(self.board)
                b.play(moves[m])
                reward = b.playout()
                if self.board.mode == "2p":
                    reward = reward[self.player]
                sum = sum + reward
            if sum > bestScore:
                bestScore = sum
                bestMove = m
        return moves[bestMove]


class UCB:
    def __init__(self, board, player, num_simulations=1000):
        self.board = board
        self.num_simulations = num_simulations
        self.player = player

    def algo(self):
        moves = self.board.legalMoves()
        sumScores = [0.0 for x in range(len(moves))]
        nbVisits = [0 for x in range(len(moves))]
        for i in range(self.num_simulations):
            bestScore = 0
            bestMove = 0
            for m in range(len(moves)):
                score = 1000000
                if nbVisits[m] > 0:
                    score = sumScores[m] / nbVisits[m] + 0.4 * math.sqrt(
                        math.log(i) / nbVisits[m]
                    )
                if score > bestScore:
                    bestScore = score
                    bestMove = m
            b = copy.deepcopy(self.board)
            b.play(moves[bestMove])
            reward = b.playout()
            if self.board.mode == "2p":
                reward = reward[self.player]
            sumScores[bestMove] += reward
            nbVisits[bestMove] += 1
        bestNbVisits = 0
        bestMove = 0
        for m in range(len(moves)):
            if nbVisits[m] > bestNbVisits:
                bestNbVisits = nbVisits[m]
                bestMove = m
        return moves[bestMove]


class UCT:
    def __init__(
        self,
        board,
        player,
        simulations_number=1000,
        exploration_constant=1.41,
        max_rollout_steps=50,
    ):
        self.board = board
        self.simulations_number = simulations_number
        self.exploration_constant = exploration_constant
        self.max_rollout_steps = max_rollout_steps
        self.player = player

    def algo(self):
        root = Node(copy.deepcopy(self.board))

        for _ in range(self.simulations_number):
            node = root
            env_copy = copy.deepcopy(root.state)

            # Selection
            while not node.untried_actions and node.children:
                node = node.best_child(self.exploration_constant)
                _, _, done, _ = env_copy.step(node.action)
                if done:
                    break

            # Expansion
            if node.untried_actions:
                action = random.choice(node.untried_actions)
                node.untried_actions.remove(action)
                _, _, done, _ = env_copy.step(action)
                new_node = Node(copy.deepcopy(env_copy), parent=node, action=action)
                node.children.append(new_node)
                node = new_node

            # Simulation
            reward = self.rollout(copy.deepcopy(env_copy))

            # Backpropagation
            while node is not None:
                node.visits += 1
                node.value += reward
                node = node.parent

        best_action = max(root.children, key=lambda child: child.visits).action
        return best_action

    def rollout(self, env):
        total_reward = 0.0
        for _ in range(self.max_rollout_steps):
            if getattr(env, "done", False):  # if env.done exists
                break
            action = random.choice(env.action_space)
            _, reward, done, _ = env.step(action)
            if self.board.mode == "2p":
                reward = reward[self.player]
            total_reward += reward
            if done:
                break
        return total_reward
