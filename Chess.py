import random

class Piece:
    def __init__(self, color, kind):
        self.color = color  # "white" or "black"
        self.kind = kind    # "P", "N", "B", "R", "Q", "K"
        self.has_moved = False

    def __str__(self):
        return self.kind.upper() if self.color == "white" else self.kind.lower()

class Board:
    def __init__(self):
        self.board = self.create_board()
        self.en_passant_target = None

    def create_board(self):
        def row(color):
            return [Piece(color, kind) for kind in "RNBQKBNR"]
        def pawns(color):
            return [Piece(color, "P") for _ in range(8)]
        return [
            row("black"),
            pawns("black"),
            [None]*8,
            [None]*8,
            [None]*8,
            [None]*8,
            pawns("white"),
            row("white")
        ]

    def print_board(self):
        print("    a  b  c  d  e  f  g  h")
        print("  +------------------------+")
        for i, row in enumerate(self.board):
            s = f"{8-i} |"
            for piece in row:
                s += f" {str(piece) if piece else '.'} "
            print(s + f"| {8-i}")
        print("  +------------------------+")
        print("    a  b  c  d  e  f  g  h")

    def get_piece(self, pos):
        x, y = pos
        return self.board[x][y]

    def set_piece(self, pos, piece):
        x, y = pos
        self.board[x][y] = piece

    def is_on_board(self, pos):
        x, y = pos
        return 0 <= x < 8 and 0 <= y < 8

    def move_piece(self, start, end):
        piece = self.get_piece(start)
        self.set_piece(end, piece)
        self.set_piece(start, None)
        if piece:
            piece.has_moved = True

    def all_pieces(self, color):
        for x in range(8):
            for y in range(8):
                p = self.board[x][y]
                if p and p.color == color:
                    yield p, (x, y)

class Game:
    def __init__(self, ai_enabled=False):
        self.board = Board()
        self.turn = 'white'
        self.ai_enabled = ai_enabled

    def pos_from_input(self, s):
        if len(s) != 2 or s[0] not in 'abcdefgh' or s[1] not in '12345678':
            raise ValueError("Format must be a-h followed by 1-8, e.g., 'e2'")
        y = ord(s[0]) - ord('a')
        x = 8 - int(s[1])
        if not (0 <= x < 8 and 0 <= y < 8):
            raise ValueError("Position out of bounds")
        return (x, y)

    def is_valid_move(self, start, end):
        piece = self.board.get_piece(start)
        if not piece or piece.color != self.turn:
            return False, "No piece of your color at the start position."
        target = self.board.get_piece(end)
        dx, dy = end[0] - start[0], end[1] - start[1]

        # Pawn logic
        direction = -1 if piece.color == 'white' else 1
        start_row = 6 if piece.color == 'white' else 1
        if piece.kind == 'P':
            # Normal move
            if dy == 0 and dx == direction and not target:
                return True, ""
            # Double move from start
            if dy == 0 and start[0] == start_row and dx == 2*direction and not target and not self.board.get_piece((start[0] + direction, start[1])):
                return True, ""
            # Capture
            if abs(dy) == 1 and dx == direction and target and target.color != piece.color:
                return True, ""
            return False, "Invalid pawn move."

        # Knight logic
        if piece.kind == 'N':
            if (abs(dx), abs(dy)) in [(2, 1), (1, 2)]:
                if not target or target.color != piece.color:
                    return True, ""
            return False, "Invalid knight move."

        # Rook logic
        if piece.kind == 'R':
            if dx == 0 or dy == 0:
                if self.is_path_clear(start, end):
                    if not target or target.color != piece.color:
                        return True, ""
            return False, "Invalid rook move."

        # Bishop logic
        if piece.kind == 'B':
            if abs(dx) == abs(dy) and self.is_path_clear(start, end):
                if not target or target.color != piece.color:
                    return True, ""
            return False, "Invalid bishop move."

        # Queen logic
        if piece.kind == 'Q':
            if (dx == 0 or dy == 0 or abs(dx) == abs(dy)) and self.is_path_clear(start, end):
                if not target or target.color != piece.color:
                    return True, ""
            return False, "Invalid queen move."

        # King logic (no castling yet)
        if piece.kind == 'K':
            if max(abs(dx), abs(dy)) == 1:
                if not target or target.color != piece.color:
                    return True, ""
            return False, "Invalid king move."

        return False, "Unknown piece type."

    def is_path_clear(self, start, end):
        dx = end[0] - start[0]
        dy = end[1] - start[1]
        steps = max(abs(dx), abs(dy))
        if steps == 0:
            return False
        x_step = (dx // steps) if dx != 0 else 0
        y_step = (dy // steps) if dy != 0 else 0
        x, y = start
        for _ in range(steps - 1):
            x += x_step
            y += y_step
            if self.board.get_piece((x, y)):
                return False
        return True

    def king_position(self, color):
        for piece, pos in self.board.all_pieces(color):
            if piece.kind == 'K':
                return pos
        return None

    def is_square_attacked(self, square, color):
        enemy = 'black' if color == 'white' else 'white'
        for piece, pos in self.board.all_pieces(enemy):
            valid, _ = self.is_valid_move(pos, square)
            if valid:
                return True
        return False

    def is_in_check(self, color):
        king_pos = self.king_position(color)
        return self.is_square_attacked(king_pos, color)

    def has_legal_moves(self, color):
        for piece, start in self.board.all_pieces(color):
            for x in range(8):
                for y in range(8):
                    end = (x, y)
                    valid, _ = self.is_valid_move(start, end)
                    if valid and self.try_move_causes_no_check(start, end):
                        return True
        return False

    def try_move_causes_no_check(self, start, end):
        piece = self.board.get_piece(start)
        target = self.board.get_piece(end)
        self.board.move_piece(start, end)
        check = self.is_in_check(piece.color)
        self.board.move_piece(end, start)
        self.board.set_piece(end, target)
        return not check

    def is_checkmate(self, color):
        return self.is_in_check(color) and not self.has_legal_moves(color)

    def is_stalemate(self, color):
        return not self.is_in_check(color) and not self.has_legal_moves(color)

    def move(self, start, end):
        self.board.move_piece(start, end)
        self.turn = 'black' if self.turn == 'white' else 'white'

    def play_turn(self):
        self.board.print_board()
        print(f"Turn: {self.turn} ({'AI' if self.ai_enabled and self.turn == 'black' else 'Player'})")
        if self.is_in_check(self.turn):
            print(f"{self.turn.capitalize()} is in check!")

        if self.ai_enabled and self.turn == 'black':
            self.play_ai()
            return

        while True:
            try:
                start = input("Enter start position (e.g. e2): ")
                end = input("Enter end position (e.g. e4): ")
                s = self.pos_from_input(start)
                e = self.pos_from_input(end)
                valid, _ = self.is_valid_move(s, e)
                if not valid or not self.try_move_causes_no_check(s, e):
                    print("Illegal move.")
                    continue
                self.move(s, e)
                break
            except ValueError as ve:
                print(ve)

    def play_ai(self):
        moves = []
        for piece, start in self.board.all_pieces('black'):
            for x in range(8):
                for y in range(8):
                    end = (x, y)
                    valid, _ = self.is_valid_move(start, end)
                    if valid and self.try_move_causes_no_check(start, end):
                        moves.append((start, end))
        if not moves:
            print("AI has no moves!")
            return
        start, end = random.choice(moves)
        print(f"AI moves from {chr(start[1]+ord('a'))}{8-start[0]} to {chr(end[1]+ord('a'))}{8-end[0]}")
        self.move(start, end)

    def run(self):
        while True:
            self.play_turn()
            if self.is_checkmate(self.turn):
                self.board.print_board()
                print(f"Checkmate! {self.turn} loses.")
                break
            if self.is_stalemate(self.turn):
                self.board.print_board()
                print("Stalemate! Draw.")
                break

if __name__ == "__main__":
    print("Welcome to Chess!")
    print("Choose mode: ")
    print("1. Human vs Human")
    print("2. Human vs AI")
    while True:
        mode = input("Enter 1 or 2: ")
        if mode == "1":
            ai_enabled = False
            break
        elif mode == "2":
            ai_enabled = True
            break
        else:
            print("Invalid input. Enter 1 or 2.")

    game = Game(ai_enabled=ai_enabled)
    game.run()
