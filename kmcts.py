# written by Kenny Lee and Jiawei Xu
# Subject COMP30024 Artificial Intelligence
import datetime
import math
import random
from watchyourback import *

PLACING = 23

class MonteCarlo(object):
    # initialise mcts
    def __init__(self, board):
        self.board = board # Game Board
        self.states = [self.board.start()] # Game States
        self.C = 5 # Larger -> More exploration, Smaller -> More exploitation
        self.calculation_time = datetime.timedelta(seconds=2)  # Calculate time
        self.max_moves = 100 # Maximum moves
        self.wins = {}
        self.plays = {}

    # Append a game state to history
    def update(self, state):
        self.states.append(state)

    # return the most optimal move based on simulation
    def get_play(self, current_turn):

        self.max_depth = 0
        # get current state
        state = self.states[-1]
        # determine player base on the number of pieces
        player = self.board.current_player(current_turn)
        legal = self.board.legal_plays(self.states[:], player)

        if not legal:
            return
        if len(legal) == 1:
            return legal[0]

        games = 0
        begin = datetime.datetime.utcnow()
        # run simulation for a certain amount of time
        while datetime.datetime.utcnow() - begin < self.calculation_time:
            self.run_simulation(current_turn)
            games+=1

        moves_states = [(move, self.board.next_state(state, move, player)) \
        for move in legal]

        # get highest win rate move
        percent_wins, move = max((self.wins.get((player, str(state)), 0)/ \
        self.plays.get((player, str(state)), 1), move) for move, state \
        in moves_states)

        # update state
        for t, S in moves_states:
            if move == t:
                self.update(self.update_state\
                (self.check_other_elimination(move, S, player), S))

        return move

    def run_simulation(self, turns):
        plays, wins = self.plays, self.wins # Dictionary of plays and wins
        visited_states = set() # Have a set of visited game states
        states_copy = self.states[:] # Copy the current sates (game history)
        state = states_copy[-1] # Get current state
        expand = True # Set expand flag to True
        current_turn = turns
        player = self.board.current_player(current_turn) # Get current player


        # Select a move using UCB1 or randomly choose from a set of legal moves
        for moves in range(1, self.max_moves + 1):
            legal = self.board.legal_plays(states_copy, player) # get all legal moves from current state
            moves_states = [(move, self.board.next_state(state, move, player)) \
            for move in legal] # From all legal moves, get the moves states

            # Check if the moves states are in the Plays (dictionary)
            if all(plays.get((player, str(state))) \
            for move, state in moves_states):

                log_total = math.log(sum(plays[(player, str(state))] \
                for move, state in moves_states))
                value, move, state = max(((wins[(player, str(state))] / \
                plays[(player, str(state))] + self.C  * math.sqrt(log_total/ \
                plays[(player, str(state))]), move, state) for move, state \
                in moves_states))

            else:

                while True:
                    move, state = random.choice(moves_states) # Random
                    # if this move is eliminate the piece it self
                    # and does not eliminate other pieces, pick another move
                    if self.check_self_elimination(move, state, player) and \
                    not self.check_other_elimination(move, state, player):
                        continue

                    else:
                        break

            # update the move to the state
            state[move] = player
            # check if this move eliminates other pieces
            eliminated_pieces = self.check_other_elimination(move, state, player)
            # elimination
            if eliminated_pieces:
                state = self.update_state(eliminated_pieces, state)
            states_copy.append(state) # Add to copied game states history
            # create a new node for the current play
            if expand and (player, str(state)) not in plays:
                expand = False
                plays[(player, str(state))] = 0
                wins[(player, str(state))] = 0
                if moves > self.max_depth:
                    self.max_depth = moves

            visited_states.add((player, str(state))) # update the visited states

            # update current turn
            current_turn += 1
            # determine next player
            player = self.board.current_player(current_turn)

            if current_turn ==  PLACING + 1:
                winner = self.board.winner(states_copy) # Check if it won

                break


        # Check if the stimulation has been run before
        for player, state in visited_states:
            if (player, state) not in plays:
                continue
            # update plays
            plays[(player, state)] += 1
            # update if the player is a winner
            if player == winner:
                wins[(player, state)] += 1

    # check if this move eliminate other pieces
    # returns a list that is eliminated
    def check_other_elimination(self, move, state, player):
        eliminated_pieces = []
        for dir in DIRECTIONS:
            adjacent_square = step(move, dir)
            opposite_square = step(adjacent_square, dir)
            if adjacent_square in state and opposite_square in state:

                if state[adjacent_square] in ENEMIES[player] and \
                state[opposite_square] in FRIENDS[player]:

                    eliminated_pieces.append(adjacent_square)
        return eliminated_pieces

    # check if this move eliminate the piece itself
    def check_self_elimination(self, move, state, player):
        for forward, backward in [(UP, DOWN), (LEFT, RIGHT)]:
            front_square = step(move, forward)
            back_square  = step(move, backward)
            if front_square in state and back_square in state:
                if state[front_square] in ENEMIES[player] \
                and state[back_square] in ENEMIES[player]:

                    return True
        return False

    # update the current state caused by elimination
    def update_state(self, eliminate_list, state):

        for square in eliminate_list:
            state[square] = BLANK

        return state





import sys
def log(*args, **kwargs):
    print(*args, file=sys.stderr, **kwargs)
