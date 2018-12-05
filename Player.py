# written by Kenny Lee and Jiawei Xu
# Subject COMP30024 Artificial Intelligence
from watchyourback import *
import math
from lin_reg import *
import random
from kmcts import *

PLACING_NUM = 12 # total number of pieces to be placed
PLACING, MOVING = 0, 1 # define phases
FIRST_SHRINK = 64 # board will shrink after player takes this turn
# INIT_STEP = 0.64

"""
the player class which defines all functions and attributes the is needed for
referee to run the simulations
"""
class Player:
    """
    attributes used in this class
    """
    color = None # player's color
    enemy_color = None # other player's color
    board = None # a inner build board
    max_depth = 5 # the maximum depth that minimax algorithm explores
    turns = 0 # current turn
    shrink_num = 0 # count how many times the board has shrinked
    phase = None # current phase
    initial_step = 0 # shrink related attribute, to generate heuritic
    MC = None # self build in MonteCarlo tree search
    step = 0 # current step

    """
    initialise player
    """
    def __init__(self, color):
        if color is "white":
            self.color = WHITE
            self.enemy_color = BLACK
        elif color is "black":
            self.color = BLACK
            self.enemy_color = WHITE

        self.setup_board()# initialise an empty board

        self.phase = PLACING # default to be placing phase

        self.MC = MonteCarlo(self.board) # Initialise MCTS

        self.initial_step = get_step(self.color) # read the highest win rate step attribute from data file


    # check whether the current player should forfeit this turn
    def forfeit(self):
        # Check if player has any pieces left
        remaining_pieces = [p for p in self.friend_pieces() if p.alive]
        if len(remaining_pieces) is 0:
            # if not, pass this turn
            return None, None
        else:
            # check whether any piece could make a move
            for piece in remaining_pieces:
                if not len(piece.moves()) is 0:
                    # default the moved piece and best move
                    return piece, piece.moves()[0]
        # if not, pass this turn
        return None, None


    # shrink board for white player
    def shrink_WHITE(self):
        guard = FIRST_SHRINK/ pow(2, self.shrink_num)
        if self.turns == guard + 1:
            self.board.shrink() # actural shrink of inner build board
            self.reset_step() # reset step value
            self.turns = 1 # shrink happens at the beginning of turn 65 for white player
            if not self.shrink_num >= 2:
                self.shrink_num += 1

    # shrink board for black player
    def shrink_BLACK(self):
        guard = FIRST_SHRINK/ pow(2, self.shrink_num)
        if self.turns == guard:
            self.board.shrink() # actural shrink of inner build board
            self.reset_step() # reset step value
            self.turns = 0 # shrink happens at the end of turn 64 for black player
            if not self.shrink_num >= 2:
                self.shrink_num += 1


    # returns an action if current phase is moving
    def move_phase(self):
        # shrink board for white player
        if self.color == WHITE:
            self.shrink_WHITE()

        self.update_step() # update step attribute

        # check forfeit, initialise which piece to move and best move
        moved_piece, best_move = self.forfeit()
        if not moved_piece or not best_move:
            return None

        # initialize alpha and beta
        alpha = float("-inf")
        beta = float("inf")

        remaining_pieces = [p for p in self.friend_pieces() if p.alive]

        for piece in remaining_pieces:
            old_pos = piece.pos
            # get all possible moves of current pieces
            for move in piece.moves():
                # make a move of a piece to a square
                eliminated_pieces = piece.makemove(move)
                # implement minimax algorithm
                current_heuristic = self.ab_minimax(move, 1, alpha, beta)
                # undo move
                piece.undomove(old_pos, eliminated_pieces)
                # iff the heuristic is higher
                if current_heuristic > alpha:
                    # update heuristic
                    alpha = current_heuristic
                    # record the square the piece moves into
                    best_move = move
                    # record current piece
                    moved_piece = piece

        pos = moved_piece.pos
        # acrtually move piece on the board:
        board_piece = self.board.find_piece(pos)
        # update the board with best move
        eliminated_pieces = board_piece.makemove(best_move)

        # shrink player's board
        if self.color == BLACK:
            self.shrink_BLACK()

        # return the coordinate of best move
        next_move = (pos, best_move)
        # to avoid extreme conditions happen in every turn
        random.shuffle(self.friend_pieces())
        random.shuffle(self.enemy_pieces())

        # check winner
        # self.check_winner()
        return next_move

    # check whether there is an enemy piece that can be removed in placing phase
    def enemy_eliminate(self):
        for piece in self.enemy_pieces():
            for forward, backward in [(UP, DOWN), (LEFT, RIGHT)]:
                front_square = step(piece.pos, forward)
                back_square  = step(piece.pos, backward)

                if not front_square in self.board.grid or \
                not back_square in self.board.grid:
                    continue
                # if a piece can be removed, return its pos
                if self.board.grid[front_square] in FRIENDS[self.color]:
                    if back_square not in self.enemy_no_zone() and \
                    self.board.grid[back_square] is BLANK:
                        return back_square
                elif self.board.grid[back_square] in FRIENDS[self.color]:
                    if front_square not in self.enemy_no_zone() and \
                    self.board.grid[front_square] is BLANK:
                        return front_square
        # if none is eliminatable, return None
        return None

    # get the area that player cannot put a piece on
    def enemy_no_zone(self):
        if self.color is BLACK:
            return self.board.black_no_zone

        else:
            return self.board.white_no_zone

    # for data collection and machine learning
    def random_place(self):
        while True:
            if self.color == BLACK:
                x = randint(0,7)
                y = randint(2,7)

            else:
                x = randint(0,7)
                y = randint(0,5)

            if not self.board.find_piece((x,y)) and not self.board.grid[(x, y)] == CORNER:
                break

        return (x,y)

    # decide which action to do in next step
    def action(self, turns):
        self.turns += 1
        next_move = None;

        # This Placing phase
        if self.phase is PLACING:
            # if any enemy piece is eliminatable
            # it gets higher priority than use mcts
            if self.enemy_eliminate():
                next_move = self.enemy_eliminate()
            else:
                next_move = self.MC.get_play(turns)

            # next_move = self.random_place()
            self.board.placing_piece(self.color, next_move)

            # update to move phase if turns have reached
            if self.turns == PLACING_NUM:
                self.phase = MOVING
                self.turns = 0

        # THis is Moving phases
        elif self.phase is MOVING:
            next_move = self.move_phase()

        return next_move


    # checks who win in a game and update the data file
    def check_winner(self):
        my_piece = 0
        enemy_piece = 0

        for piece in self.friend_pieces():
            if piece.alive:
                my_piece += 1
        if my_piece < 2 and self.color is WHITE:
            update_file(INIT_STEP, False, self.color)
        elif my_piece < 2 and self.color is BLACK:
            update_file(INIT_STEP, True, self.enemy_color)


        for piece in self.enemy_pieces():
            if piece.alive:
                enemy_piece += 1
        if enemy_piece < 2 and self.color is WHITE:
            update_file(INIT_STEP, True, self.color)
        elif enemy_piece < 2 and self.color is BLACK:
            update_file(INIT_STEP, False, self.enemy_color)



    # check the number of pieces remained on the board
    # and return heuristic based on number
    def Material(self, weight):
        heuristic = 0
        for piece in self.friend_pieces():
            if piece.alive:
                heuristic += 1

        for piece in self.enemy_pieces():
            if piece.alive:
                heuristic -= 1
        # calculate heuristic by difference of friend_pieces and enemy_pieces
        return heuristic * weight

    # set step to 0 after board shrinks
    def reset_step(self):
        self.step = 0

    def update_step(self):
        self.step = round(self.turns*(pow(2, self.shrink_num)*\
        self.initial_step),2)


    # return a heuristic based on number of pieces on the squares
    # which are going to be removed at next shrink
    def Boundary(self):

        heuristic = 0
        # get all squares that is gonna be removed at next board shrink
        squareList = self.board.shrink_squares()
        hot_spot = self.board.Hot_Spot((BOARD_SIZE - self.board.size) / 2 + 1)
        # lower heuristic if more friend_pieces
        for piece in self.friend_pieces():
            if piece.pos in squareList + hot_spot and piece.alive:
                heuristic -= self.step

        return heuristic


    # evaluation function used at the leaf of minimax algorithm
    def get_heuristic(self):
        total = 0
        total += self.Material(100) # Number of Pieces
        total += self.Boundary() # Shrink Zone

        return total


    # simple minimax algorithm
    def ab_minimax(self, pos, current_depth, alpha, beta):
        # increase depth
        current_depth += 1

        # if max_depth is reached
        if current_depth == self.max_depth:
            # apply evaluation function
            return self.get_heuristic()

        if current_depth % 2 == 0:
            # min player's turn
            # loop all enemy pieces of our player
            remaining_pieces = [p for p in self.enemy_pieces() if p.alive]
            for piece in remaining_pieces:

                possible_moves = piece.moves()
                # check if this piece can move
                if len(possible_moves) == 0:
                    continue
                else:
                    for new_pos in possible_moves:
                        # record old_pos for undomove
                        old_pos = piece.pos
                        # do alpha beta pruning
                        if alpha < beta:
                            # move the piece into the aim square
                            eliminated_pieces = piece.makemove(new_pos)
                            current_heuristic = self.ab_minimax(new_pos, current_depth, alpha, beta)
                            # undo move
                            piece.undomove(old_pos, eliminated_pieces)
                            # update beta
                            if beta > current_heuristic:
                                beta = current_heuristic
            return beta

        else:
            # max player's turn
            # loop all friend pieces of our player
            remaining_pieces = [p for p in self.friend_pieces() if p.alive]
            for piece in remaining_pieces:

                possible_moves = piece.moves()
                # check if this piece can move
                if len(possible_moves) == 0:
                    continue
                else:
                    for new_pos in possible_moves:
                        # record old_pos for undo
                        old_pos = piece.pos
                        # do alpha beta pruning
                        if alpha < beta:
                            # move the piece into the aim square
                            eliminated_pieces = piece.makemove(new_pos)
                            current_heuristic = self.ab_minimax(new_pos, current_depth, alpha, beta)
                            # undo move
                            piece.undomove(old_pos, eliminated_pieces)
                            # update alpha
                            if alpha < current_heuristic:
                                alpha = current_heuristic
            return alpha


    # receive an action from the other player and update inner build board
    def update(self, action):
        # forfeit
        if action is None:
            return
        # this is a placing
        if isinstance(action[0], int):
            self.board.placing_piece(self.enemy_color, action)
            self.MC.update(self.board.grid)
        # this is a moving
        else:
            self.board.moving_piece(action)

        return

    # returns all enemy pieces from board
    def enemy_pieces(self):
        if self.color is WHITE:
            return self.board.black_pieces
        elif self.color is BLACK:
            return self.board.white_pieces
        return

    # returns all friend pieces from board
    def friend_pieces(self):
        if self.color is WHITE:
            return self.board.white_pieces
        elif self.color is BLACK:
            return self.board.black_pieces
        return

    # initialise board
    def setup_board(self):
        self.board = Board(self.color)
        return


import sys
def log(*args, **kwargs):
    print(*args, file=sys.stderr, **kwargs)
