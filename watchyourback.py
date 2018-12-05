import datetime
"""
Author: Matt Farrugia <matt.farrugia@unimelb.edu.au>
April 2018

"""
# HELPERS

WHITE, BLACK, CORNER, BLANK, REMOVED = ['O','@','X','-',' ']
ENEMIES = {WHITE: {BLACK, CORNER}, BLACK: {WHITE, CORNER}}
FRIENDS = {WHITE: {WHITE, CORNER}, BLACK: {BLACK, CORNER}}
BOARD_SIZE = 8

CORNERS = [(0, 0), (BOARD_SIZE - 1, 0), (0, BOARD_SIZE - 1), \
(BOARD_SIZE - 1, BOARD_SIZE - 1)]

DIRECTIONS = UP, DOWN, LEFT, RIGHT = (0, -1), (0, 1), (-1, 0), (1, 0)

def step(position, direction):
    """
    Take an (x, y) tuple `position` and a `direction` (UP, DOWN, LEFT or RIGHT)
    and combine to produce a new tuple representing a position one 'step' in
    that direction from the original position.
    """
    px, py = position
    dx, dy = direction
    return (px+dx, py+dy)

# CLASSES

class Board:
    player = None
    white_no_zone = [] # area white player cannot put a piece on
    black_no_zone = [] # area black player cannot put a piece on
    start_state = {} # same as grid

    def __init__(self, player, data = None):
        # Restricted Area for Placing
        for y in range(BOARD_SIZE):
            for x in range(BOARD_SIZE):
                if y == 0 or y==1:
                    self.black_no_zone.append((x,y))

                if y == BOARD_SIZE -2 or y == BOARD_SIZE -1:
                    self.white_no_zone.append((x,y))

        # Gettinig the Board
        if data is None:
            self.player = player
            self.size = BOARD_SIZE
            self.grid = {}
            self.white_pieces = []
            self.black_pieces = []
            for y in range(BOARD_SIZE):
                for x in range(BOARD_SIZE):
                    self.grid[x, y] = BLANK
                    self.set_corner(self.get_corner(0))
        else:
            self.size = len(data)
            self.grid = {}
            self.white_pieces = []
            self.black_pieces = []
            for y, row in enumerate(data):
                for x, char in enumerate(row):
                    self.grid[x, y] = char
                    if char == WHITE:
                        self.white_pieces.append(Piece(WHITE, (x, y), self))
                    if char == BLACK:
                        self.black_pieces.append(Piece(BLACK, (x, y), self))

        self.start_state = self.grid.copy() # Make a copy of the start state


    def __str__(self):
        """Compute a string representation of the board's current state."""
        ran = range(self.size)
        return '\n'.join(' '.join(self.grid[x,y] for x in ran) for y in ran)


    """ Monte Carlo Helper Functions """
    # Returns a representation of the starting state of the game.
    def start(self):
        return self.start_state


    def current_player(self, current_turn):
        if current_turn % 2 == 0:
            # Even is white
            return WHITE

        else:
            # Odd is black
            return BLACK

    def next_state(self, state, tuple, player):
        # Takes the game state, and the move to be applied.
        # Returns the new game state.
        # State is in grid

        new_state = state.copy()
        new_state[tuple] = player

        return new_state

    # get all legal move for the current player
    def legal_plays(self, state_history, player):
        legal_plays = []
        current_state = state_history[-1]

        for tuple, piece in current_state.items():
            if piece is BLANK:
                if player is WHITE and tuple not in self.white_no_zone:
                        legal_plays.append(tuple)


                elif player is BLACK and tuple not in self.black_no_zone:
                        legal_plays.append(tuple)

        return legal_plays


    def winner(self, state_history):
        # Takes a sequence of game states representing the full
        # game history.  If the game is now won, return the player
        # number.  If the game is still ongoing, return zero.  If
        # the game is tied, return a different distinct value, e.g. -1.

        current_state = state_history[-1]
        num_white = 0
        num_black = 0


        for tuple in current_state:
            if current_state[tuple] is WHITE:
                num_white += 1
            elif current_state[tuple] is BLACK:
                num_black += 1

        if num_white > num_black:
            return WHITE
        else:
            return BLACK


    def find_piece(self, square):
        """
        An O(n) operation (n = number of pieces) to find the piece object
        for the piece occupying a given position on the board. This method
        could be improved by separately keeping track of which piece is at
        each position.
        """
        for piece in self.black_pieces + self.white_pieces:
            if piece.pos == square and piece.alive:
                return piece

    # placing a piece of given color to a given square(action)
    def placing_piece(self, color, action):

        x, y = action
        self.grid[x, y] = color
        if color is WHITE:
            piece = Piece(WHITE, (x, y), self)
            self.white_pieces.append(piece)
            # check elimination of this placing
            piece.makemove((x, y))

        if color is BLACK:
            piece = Piece(BLACK, (x, y), self)
            self.black_pieces.append(piece)
            piece.makemove((x, y))

    # move a piece from an old square to a new one given by the pos in action
    def moving_piece(self, action):
        old_pos, new_pos = action

        piece = self.find_piece(old_pos)
        if piece:
            # check elimination due to this move
            piece.makemove(new_pos)


    # shrink the board
    def shrink(self):
        # Get the list of squares that is to be eliminated
        squareList = self.shrink_squares()

        # Set the squares to be eliinated as REMOVED
        self.set_squares(squareList, REMOVED)

        # Reduce the board size by 2
        self.size -= 2

        # Get new corners
        self.set_corner(self.get_corner((BOARD_SIZE - self.size) / 2))


    # Replace the squares in a list to either a REMOVED or CORNER
    def set_squares(self, squareList, set):

        for piece in self.white_pieces + self.black_pieces:
            if piece.pos in squareList and piece.alive:
                piece.eliminate()

        for square in squareList:
            self.grid[square] = set

        return


    # Return the outer parameters that is going to be eliminated
    def shrink_squares(self):

        squareList = []

        lo = int((BOARD_SIZE - self.size)/2)
        hi = int(BOARD_SIZE - ((BOARD_SIZE - self.size)/2) - 1)

        for num in range(lo, hi + 1):

            squareList.append((num, lo))
            squareList.append((lo, num))
            squareList.append((num, hi))
            squareList.append((hi, num))


        return squareList

    # Establish a corner
    def set_corner(self, corners):

        self.set_squares(corners, CORNER)

        # check elimination due to reset of corners
        for piece in self.white_pieces + self.black_pieces:
            if piece.alive:
                piece.makemove(piece.pos)

        return

    # get new_corners that forms in next shrink
    def get_corner(self, degree):

        lo = 0
        hi = 0
        new_corners = []

        degree = int(degree)

        for tuple in CORNERS:
            lo = min(tuple)
            hi = max(tuple)

            if not lo == hi:
                break

        new_corners.append((lo + degree, lo + degree))
        new_corners.append((lo + degree, hi - degree))
        new_corners.append((hi - degree, lo + degree))
        new_corners.append((hi - degree, hi - degree))

        return new_corners

    # disadvantage positions around corners are evaluated same as corners
    def Hot_Spot(self, degree):
        new_corners = self.get_corner(degree)
        hot_spot = []

        for corner in new_corners:
            for dir in DIRECTIONS:
                adjacent_square = step(corner, dir)
                hot_spot.append(corner)
                hot_spot.append(adjacent_square)

        return hot_spot

class Piece:
    """
    A class to represent a Watch Your Back! piece somewhere on a game board.

    This piece tracks its type (BLACK or WHITE, in `player`) and its current
    position (an (x, y) tuple, in `pos`). It also keeps track of whether or not
    it is currently on the board (Boolean value, in `alive`).

    Contains methods for analysing or changing the piece's current position.
    """
    def __init__(self, player, pos, board):
        """
        Create a new piece for a particular player (BLACK or WHITE) currently
        at a particular position `pos` on board `board`. This piece starts out
        in the `alive = True` state and changes to `alive = False` when it is
        eliminated.
        """
        self.player = player
        self.pos = pos
        self.board = board
        self.alive = True
    def __str__(self):
        return
    def __repr__(self):
        return
    def __eq__(self, other):
        return (self.player, self.pos) == (other.player, other.pos)

    def moves(self):
        """
        Compute and return a list of the available moves for this piece based
        on the current board state.

        Do not call with method on pieces with `alive = False`.
        """

        possible_moves = []
        for direction in DIRECTIONS:
            # a normal move to an adjacent square?
            adjacent_square = step(self.pos, direction)
            if adjacent_square in self.board.grid:
                if self.board.grid[adjacent_square] == BLANK:
                    possible_moves.append(adjacent_square)
                    continue # a jump move is not possible in this direction

            # if not, how about a jump move to the opposite square?
            opposite_square = step(adjacent_square, direction)
            if opposite_square in self.board.grid:
                if self.board.grid[opposite_square] == BLANK:
                    possible_moves.append(opposite_square)
        return possible_moves

    def makemove(self, newpos):
        """
        Carry out a move from this piece's current position to the position
        `newpos` (a position from the list returned from the `moves()` method)
        Update the board including eliminating any nearby pieces surrounded as
        a result of this move.

        Return a list of pieces eliminated by this move (to be passed back to
        the `undomove()` method if you want to reverse this move).

        Do not call with method on pieces with `alive = False`.
        """
        # make the move
        oldpos = self.pos
        self.pos = newpos
        self.board.grid[oldpos] = BLANK
        self.board.grid[newpos] = self.player

        # eliminate any newly surrounded pieces
        eliminated_pieces = []

        # check adjacent squares: did this move elimminate anyone?
        for direction in DIRECTIONS:
            adjacent_square = step(self.pos, direction)
            opposite_square = step(adjacent_square, direction)
            if opposite_square in self.board.grid:
                if self.board.grid[adjacent_square] in ENEMIES[self.player] \
                and self.board.grid[opposite_square] in FRIENDS[self.player]:
                    eliminated_piece = self.board.find_piece(adjacent_square)
                    eliminated_piece.eliminate()
                    eliminated_pieces.append(eliminated_piece)

        # check horizontally and vertically: does the piece itself get
        # eliminated?
        for forward, backward in [(UP, DOWN), (LEFT, RIGHT)]:
            front_square = step(self.pos, forward)
            back_square  = step(self.pos, backward)
            if front_square in self.board.grid \
            and back_square in self.board.grid:
                if self.board.grid[front_square] in ENEMIES[self.player] \
                and self.board.grid[back_square] in ENEMIES[self.player]:
                    self.eliminate()
                    eliminated_pieces.append(self)
                    break

        return eliminated_pieces

    def undomove(self, oldpos, eliminated_pieces):
        """
        Roll back a move for this piece to its previous position `oldpos`,
        restoring the pieces it had eliminated `eliminated_pieces` (a list as
        returned from the `makemove()` method).

        A move should only be 'undone' if no other moves have been made since
        (unless they have already been 'undone' also).

        Do not call with method on pieces with `alive = False` unless you are
        undoing the move that eliminated this piece.
        """
        # put back the pieces that were eliminated
        for piece in eliminated_pieces:
            piece.resurrect()

        # undo the move itself
        newpos = self.pos
        self.pos = oldpos
        self.board.grid[newpos] = BLANK
        self.board.grid[oldpos] = self.player

    def eliminate(self):
        """
        Set a piece's state to `alive = False` and remove it from the board
        For internal use only.
        """
        self.alive = False
        self.board.grid[self.pos] = BLANK

    def resurrect(self):
        """
        Set a piece's state to `alive =`` True` and restore it to the board
        For internal use only.
        """
        self.alive = True
        self.board.grid[self.pos] = self.player


import sys
def log(*args, **kwargs):
    print(*args, file=sys.stderr, **kwargs)
