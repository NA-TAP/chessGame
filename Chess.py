class ChessGame:
    def __init__(self):
        self.board = self.create_board()
        self.turn = 'white'

    def create_board(self):
        return [
            ['r', 'n', 'b', 'q', 'k', 'b', 'n', 'r'],
            ['p', 'p', 'p', 'p', 'p', 'p', 'p', 'p'],
            [' ', ' ', ' ', ' ', ' ', ' ', ' ', ' '],
            [' ', ' ', ' ', ' ', ' ', ' ', ' ', ' '],
            [' ', ' ', ' ', ' ', ' ', ' ', ' ', ' '],
            [' ', ' ', ' ', ' ', ' ', ' ', ' ', ' '],
            ['P', 'P', 'P', 'P', 'P', 'P', 'P', 'P'],
            ['R', 'N', 'B', 'Q', 'K', 'B', 'N', 'R'],
        ]

    def print_board(self):
        for row in self.board:
            print(' '.join(row))

    def move_piece(self, start, end):
        sx, sy = self.convert_to_index(start)
        ex, ey = self.convert_to_index(end)
        if self.is_valid_move(sx, sy, ex, ey):
            self.board[ex][ey] = self.board[sx][sy]
            self.board[sx][sy] = ' '
            self.change_turn()
        else:
            print("Invalid move. Try again.")

    def convert_to_index(self, pos):
        col, row = pos
        return 8 - int(row), ord(col) - ord('a')

    def is_valid_move(self, sx, sy, ex, ey):
        # Simplified move validation, you can expand this with actual chess rules
        return self.board[sx][sy].lower() in 'rnbqkp'

    def change_turn(self):
        self.turn = 'black' if self.turn == 'white' else 'white'

    def run(self):
        while True:
            self.print_board()
            start = input(f"{self.turn}'s turn. Enter the start position (e.g., 'e2'): ")
            end = input(f"Enter the end position (e.g., 'e4'): ")
            self.move_piece(start, end)


if __name__ == "__main__":
    game = ChessGame()
    game.run()
