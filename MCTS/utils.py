import numpy as np
from MCTS.elements import Board

def deepcopy_board(board):
    new_board = Board()
    new_board.board = np.copy(board.board)
    new_board.turn = board.turn
    new_board.h = board.h
    return new_board
