'''Chess by anay.taparia@gmail.com
8x8x2 3D board version with board ! and board @'''
import sys
WIDTH = 8
HEIGHT = 8
BLANK = ' '
WHITE = "white"
BLACK = "black"
BOARD_BOTTOM = 0  # board !
BOARD_TOP = 1     # board @


def square_to_coord(square):
    if len(square) != 2:
        raise ValueError("invalid square")
    file = square[0].lower()
    rank = square[1]
    if file < 'a' or file > 'h' or rank < '1' or rank > '8':
        raise ValueError("invalid square")
    return ord(file) - ord('a'), int(rank) - 1


class Piece:
    def __init__(self, kind, color):
        self.kind = kind
        self.color = color

    def __str__(self):
        return self.kind.upper() if self.color == WHITE else self.kind.lower()

    def get_unicode_str(self):
        str_to_unicode_W = {"K": "♚", "Q": "♛", "R": "♜", "B": "♝", "N": "♞", "P": "♟"}
        str_to_unicode_B = {"K": "♔", "Q": "♕", "R": "♖", "B": "♗", "N": "♘", "P": "♙"}
        return str_to_unicode_W[self.kind] if self.color == WHITE else str_to_unicode_B[self.kind]


class Board:
    def __init__(self, turn=WHITE):
        self.layers = [self.new_board(), self.empty_board()]
        self.turn = turn

    def new_board(self):
        return [
            [Piece('R', WHITE), Piece('N', WHITE), Piece('B', WHITE), Piece('Q', WHITE), Piece('K', WHITE), Piece('B', WHITE), Piece('N', WHITE), Piece('R', WHITE)],
            [Piece('P', WHITE), Piece('P', WHITE), Piece('P', WHITE), Piece('P', WHITE), Piece('P', WHITE), Piece('P', WHITE), Piece('P', WHITE), Piece('P', WHITE)],
            [None] * WIDTH,
            [None] * WIDTH,
            [None] * WIDTH,
            [None] * WIDTH,
            [Piece('P', BLACK), Piece('P', BLACK), Piece('P', BLACK), Piece('P', BLACK), Piece('P', BLACK), Piece('P', BLACK), Piece('P', BLACK), Piece('P', BLACK)],
            [Piece('R', BLACK), Piece('N', BLACK), Piece('B', BLACK), Piece('Q', BLACK), Piece('K', BLACK), Piece('B', BLACK), Piece('N', BLACK), Piece('R', BLACK)],
        ]

    def empty_board(self):
        return [[None] * WIDTH for _ in range(HEIGHT)]

    def print_board(self):
        rowsep = '  +---+---+---+---+---+---+---+---+'
        header = '    a   b   c   d   e   f   g   h'
        print('Board @ (top layer)'.ljust(40) + 'Board ! (bottom layer)')
        print(header + '     ' + header)
        print(rowsep + '     ' + rowsep)
        for rank in range(HEIGHT - 1, -1, -1):
            top_line = f"{rank + 1} |"
            bottom_line = f"{rank + 1} |"
            for file in range(WIDTH):
                top_piece = self.layers[BOARD_TOP][rank][file]
                bottom_piece = self.layers[BOARD_BOTTOM][rank][file]
                top_line += f" {top_piece.get_unicode_str()} " if top_piece else '   '
                top_line += '|'
                bottom_line += f" {bottom_piece.get_unicode_str()} " if bottom_piece else '   '
                bottom_line += '|'
            print(top_line + '     ' + bottom_line)
            print(rowsep + '     ' + rowsep)


class Move:
    def __init__(self, move_str):
        move_str = move_str.strip()
        if move_str.endswith('@@'):
            self.s_layer = BOARD_BOTTOM
            self.d_layer = BOARD_TOP
            self.sf, self.sr = square_to_coord(move_str[:2])
            self.ef, self.er = self.sf, self.sr
        elif move_str.endswith('!!'):
            self.s_layer = BOARD_TOP
            self.d_layer = BOARD_BOTTOM
            self.sf, self.sr = square_to_coord(move_str[:2])
            self.ef, self.er = self.sf, self.sr
        elif len(move_str) == 4:
            self.s_layer = BOARD_BOTTOM
            self.d_layer = BOARD_BOTTOM
            self.sf, self.sr = square_to_coord(move_str[:2])
            self.ef, self.er = square_to_coord(move_str[2:])
        else:
            raise ValueError('invalid move format')

    def unpck(self):
        return self.s_layer, self.sf, self.sr, self.d_layer, self.ef, self.er


class Game:
    def __init__(self):
        self.board = Board()

    def get_input(self):
        while True:
            move = input(
                "enter your move or 'quit'\n"
                "- normal board move (board !): e2e4\n"
                "- move from board ! to board @ : e5@@\n"
                "- move from board @ to board ! : e5!!\n> "
            )
            if move == 'quit':
                sys.exit()
            try:
                move = Move(move)
                return move
            except Exception:
                print("invalid move")

    def make_move(self, move):
        s_layer, sf, sr, d_layer, ef, er = move.unpck()
        source_piece = self.board.layers[s_layer][sr][sf]
        if source_piece is None:
            print('no piece at source square')
            return

        self.board.layers[d_layer][er][ef] = source_piece
        self.board.layers[s_layer][sr][sf] = None

    def main(self):
        while True:
            self.board.print_board()
            move = self.get_input()
            self.make_move(move)


if __name__ == "__main__":
    chess = Game()
    chess.main()


