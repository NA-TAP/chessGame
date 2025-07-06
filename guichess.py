import tkinter as tk
from tkinter import messagebox
import copy # Used for deep copying the board for move simulations

class ChessGame:
    def __init__(self, master):
        self.master = master
        self.master.title("Unicode Chess")
        self.master.geometry("640x680") # Slightly larger to accommodate status text

        self.canvas = tk.Canvas(master, width=640, height=640, bg="lightgray")
        self.canvas.pack(pady=10) # Add some padding

        self.status_label = tk.Label(master, text="White's Turn", font=("Inter", 14, "bold"))
        self.status_label.pack()

        self.square_size = 80
        self.board_colors = {"light": "#F0D9B5", "dark": "#B58863"} # Standard chess board colors
        self.piece_colors = {"white": "white", "black": "black"} # Text colors for the pieces
        self.highlight_color = "#FFFF00" # Yellow for selected piece
        self.valid_move_highlight_color = "#A7C7E7" # Light blue for valid moves
        self.check_highlight_color = "#FF0000" # Red for King in check

        # Unicode characters for black pieces (used for both players, differentiated by text color)
        self.unicode_pieces = {
            'K': '\u265A', # Black King
            'Q': '\u265B', # Black Queen
            'R': '\u265C', # Black Rook
            'B': '\u265D', # Black Bishop
            'N': '\u265E', # Black Knight
            'P': '\u265F'  # Black Pawn
        }

        # Initial board setup (piece_type, player_color)
        self.board = [
            [('R', 'black'), ('N', 'black'), ('B', 'black'), ('Q', 'black'), ('K', 'black'), ('B', 'black'), ('N', 'black'), ('R', 'black')],
            [('P', 'black'), ('P', 'black'), ('P', 'black'), ('P', 'black'), ('P', 'black'), ('P', 'black'), ('P', 'black'), ('P', 'black')],
            [None, None, None, None, None, None, None, None],
            [None, None, None, None, None, None, None, None],
            [None, None, None, None, None, None, None, None],
            [None, None, None, None, None, None, None, None],
            [('P', 'white'), ('P', 'white'), ('P', 'white'), ('P', 'white'), ('P', 'white'), ('P', 'white'), ('P', 'white'), ('P', 'white')],
            [('R', 'white'), ('N', 'white'), ('B', 'white'), ('Q', 'white'), ('K', 'white'), ('B', 'white'), ('N', 'white'), ('R', 'white')]
        ]

        self.selected_piece = None # Stores (row, col) of the selected piece
        self.current_turn = 'white' # 'white' or 'black'

        # Track if King or Rooks have moved for castling
        self.has_moved = {
            'white_king': False,
            'black_king': False,
            'white_rook_kingside': False,  # Rook at (7, 7)
            'white_rook_queenside': False, # Rook at (7, 0)
            'black_rook_kingside': False,  # Rook at (0, 7)
            'black_rook_queenside': False  # Rook at (0, 0)
        }

        self.draw_board()
        self.canvas.bind("<Button-1>", self.on_square_click)

    def draw_board(self):
        """Draws the chessboard squares and pieces, including check/checkmate highlights."""
        self.canvas.delete("all") # Clear previous drawings

        for r in range(8):
            for c in range(8):
                x1, y1 = c * self.square_size, r * self.square_size
                x2, y2 = x1 + self.square_size, y1 + self.square_size
                color = self.board_colors["light"] if (r + c) % 2 == 0 else self.board_colors["dark"]
                self.canvas.create_rectangle(x1, y1, x2, y2, fill=color, outline="")

                piece_info = self.board[r][c]
                if piece_info:
                    piece_type, player_color = piece_info
                    unicode_char = self.unicode_pieces.get(piece_type)
                    if unicode_char:
                        # Draw the Unicode character with the specified text color
                        self.canvas.create_text(
                            x1 + self.square_size / 2, y1 + self.square_size / 2,
                            text=unicode_char,
                            font=("Inter", 48), # Large font size for visibility
                            fill=self.piece_colors[player_color],
                            tags=f"piece_{r}_{c}" # Tag for easy identification
                        )
        self.update_status()

        # Highlight King if in check
        if self.is_in_check(self.current_turn, self.board):
            king_pos = self._find_king_position(self.current_turn, self.board)
            if king_pos:
                r, c = king_pos
                self.highlight_square(r, c, self.check_highlight_color)
                # Bring king piece to front so it's visible over highlight
                piece_id = self.canvas.find_withtag(f"piece_{r}_{c}")
                if piece_id:
                    self.canvas.tag_raise(piece_id)

        # Check for checkmate/stalemate after drawing the board
        if self.is_in_check(self.current_turn, self.board) and self.is_checkmate(self.current_turn):
            king_pos = self._find_king_position(self.current_turn, self.board)
            if king_pos:
                r, c = king_pos
                # Position the hash sign on the king's square, slightly offset for visibility
                hash_x = c * self.square_size + self.square_size - 10 # Near top-right of square
                hash_y = r * self.square_size + 10 # Near top-right of square

                # Draw a small contrasting background rectangle for the hash
                bg_rect_id = self.canvas.create_rectangle(
                    hash_x - 20, hash_y - 20, hash_x + 20, hash_y + 20,
                    fill="black", outline="", tags="checkmate_sign_bg"
                )
                self.canvas.tag_raise(bg_rect_id) # Ensure background is behind hash but above piece

                hash_id = self.canvas.create_text(hash_x, hash_y, text="#", font=("Inter", 36, "bold"), fill="red", tags="checkmate_sign")
                self.canvas.tag_raise(hash_id) # Ensure the hash is on top

                self.status_label.config(text=f"Checkmate! {('Black' if self.current_turn == 'white' else 'White')}'s Wins!", fg="red")
        elif not self.is_in_check(self.current_turn, self.board) and self.is_stalemate(self.current_turn):
            self.status_label.config(text="Stalemate! It's a Draw!", fg="blue")


    def update_status(self):
        """Updates the status label to show whose turn it is."""
        status_text = f"{self.current_turn.capitalize()}'s Turn"
        if self.is_in_check(self.current_turn, self.board):
            status_text += " (Check!)"
            self.status_label.config(text=status_text, fg="red")
        else:
            self.status_label.config(text=status_text, fg="black")

    def on_square_click(self, event):
        """Handles a click event on the canvas."""
        col = event.x // self.square_size
        row = event.y // self.square_size

        if not (0 <= row < 8 and 0 <= col < 8):
            return # Click outside board

        piece_info = self.board[row][col]

        if self.selected_piece:
            # A piece is already selected, try to move
            selected_row, selected_col = self.selected_piece
            selected_piece_info = self.board[selected_row][selected_col]

            if selected_piece_info and self.is_valid_move(selected_row, selected_col, row, col):
                # Valid move, perform it
                self.move_piece(selected_row, selected_col, row, col)
                self.selected_piece = None
                self.clear_highlights()
                self.switch_turn()
                self.draw_board() # Redraw board after move
            elif piece_info and piece_info[1] == self.current_turn:
                # Clicked on another piece of the current player, re-select
                self.clear_highlights()
                self.selected_piece = (row, col)
                self.highlight_square(row, col, self.highlight_color)
                self.highlight_valid_moves(row, col)
            else:
                # Invalid move or clicked on opponent's piece/empty square, deselect
                self.selected_piece = None
                self.clear_highlights()
                self.draw_board() # Redraw to clear any lingering highlights
        else:
            # No piece selected, try to select one
            if piece_info and piece_info[1] == self.current_turn:
                self.selected_piece = (row, col)
                self.highlight_square(row, col, self.highlight_color)
                self.highlight_valid_moves(row, col)

    def highlight_square(self, r, c, color):
        """Highlights a specific square on the board."""
        x1, y1 = c * self.square_size, r * self.square_size
        x2, y2 = x1 + self.square_size, y1 + self.square_size
        self.canvas.create_rectangle(x1, y1, x2, y2, fill=color, outline="", tags="highlight")
        # Bring piece to front if there is one
        piece_id = self.canvas.find_withtag(f"piece_{r}_{c}")
        if piece_id:
            self.canvas.tag_raise(piece_id)

    def clear_highlights(self):
        """Removes all highlights from the board."""
        self.canvas.delete("highlight")
        self.canvas.delete("checkmate_sign") # Also clear checkmate sign
        self.canvas.delete("checkmate_sign_bg") # Clear the background rectangle too


    def highlight_valid_moves(self, r, c):
        """Highlights all valid moves for the selected piece."""
        for target_r in range(8):
            for target_c in range(8):
                # Use the full is_valid_move which includes self-check prevention
                if self.is_valid_move(r, c, target_r, target_c):
                    self.highlight_square(target_r, target_c, self.valid_move_highlight_color)

    def move_piece(self, start_row, start_col, end_row, end_col):
        """Moves a piece from start to end position on the board."""
        piece_to_move = self.board[start_row][start_col]
        piece_type, player_color = piece_to_move

        # Handle castling: if King moved two squares horizontally
        if piece_type == 'K' and abs(start_col - end_col) == 2:
            rook_start_col = -1
            rook_end_col = -1
            if end_col == start_col + 2: # Kingside castling
                rook_start_col = 7
                rook_end_col = 5
            elif end_col == start_col - 2: # Queenside castling
                rook_start_col = 0
                rook_end_col = 3

            # Perform rook move for castling
            if rook_start_col != -1:
                rook_piece = self.board[start_row][rook_start_col]
                self.board[start_row][rook_end_col] = rook_piece
                self.board[start_row][rook_start_col] = None
                # Mark the moved rook as "moved"
                if player_color == 'white':
                    if rook_start_col == 7: self.has_moved['white_rook_kingside'] = True
                    elif rook_start_col == 0: self.has_moved['white_rook_queenside'] = True
                elif player_color == 'black':
                    if rook_start_col == 7: self.has_moved['black_rook_kingside'] = True
                    elif rook_start_col == 0: self.has_moved['black_rook_queenside'] = True

        self.board[end_row][end_col] = piece_to_move
        self.board[start_row][start_col] = None

        # Update has_moved status for King and Rooks
        if piece_type == 'K':
            self.has_moved[f"{player_color}_king"] = True
        elif piece_type == 'R':
            if player_color == 'white':
                if start_row == 7 and start_col == 0:
                    self.has_moved['white_rook_queenside'] = True
                elif start_row == 7 and start_col == 7:
                    self.has_moved['white_rook_kingside'] = True
            elif player_color == 'black':
                if start_row == 0 and start_col == 0:
                    self.has_moved['black_rook_queenside'] = True
                elif start_row == 0 and start_col == 7:
                    self.has_moved['black_rook_kingside'] = True


    def switch_turn(self):
        """Switches the current player's turn."""
        self.current_turn = 'black' if self.current_turn == 'white' else 'white'
        self.update_status()

    def is_valid_move(self, start_r, start_c, end_r, end_c):
        """
        Checks if a move from (start_r, start_c) to (end_r, end_c) is valid
        according to basic chess rules for the piece type and if it leaves the king in check.
        """
        piece_info = self.board[start_r][start_c]
        if not piece_info:
            return False # No piece at start position

        piece_type, player_color = piece_info
        target_piece_info = self.board[end_r][end_c]

        # Cannot move to the same square
        if start_r == end_r and start_c == end_c:
            return False

        # Cannot capture your own piece
        if target_piece_info and target_piece_info[1] == player_color:
            return False

        # Check if the move is valid based on piece movement rules
        if not self._is_valid_move_pattern(start_r, start_c, end_r, end_c, self.board, self.has_moved):
            return False

        # Simulate the move to check if it leaves the king in check
        temp_board = copy.deepcopy(self.board)
        temp_board[end_r][end_c] = temp_board[start_r][start_c]
        temp_board[start_r][start_c] = None

        # Special handling for castling simulation: move the rook too
        if piece_type == 'K' and abs(start_c - end_c) == 2:
            if end_c == start_c + 2: # Kingside castling
                temp_board[start_r][5] = temp_board[start_r][7]
                temp_board[start_r][7] = None
            elif end_c == start_c - 2: # Queenside castling
                temp_board[start_r][3] = temp_board[start_r][0]
                temp_board[start_r][0] = None

        if self.is_in_check(player_color, temp_board):
            return False # Move would leave own king in check

        return True

    def _is_valid_move_pattern(self, start_r, start_c, end_r, end_c, board, has_moved_state):
        """
        Checks if a move is valid based purely on the piece's movement pattern,
        without considering whose turn it is or if it leaves the king in check.
        This is used for both regular moves and for checking attacks for 'is_in_check'.
        `board` and `has_moved_state` are passed explicitly for simulation purposes.
        """
        piece_info = board[start_r][start_c]
        if not piece_info:
            return False

        piece_type, player_color = piece_info
        target_piece_info = board[end_r][end_c]

        # Cannot move to the same square (already handled in is_valid_move, but good for robustness)
        if start_r == end_r and start_c == end_c:
            return False

        # Cannot capture your own piece (already handled in is_valid_move, but good for robustness)
        if target_piece_info and target_piece_info[1] == player_color:
            return False

        # --- Piece-specific move validation ---
        if piece_type == 'P': # Pawn
            direction = 1 if player_color == 'black' else -1 # Black moves down, White moves up
            
            # Normal move
            if start_c == end_c and end_r == start_r + direction and not target_piece_info:
                return True
            # Initial two-square move
            if (player_color == 'black' and start_r == 1 and end_r == start_r + 2 * direction and start_c == end_c and not target_piece_info and not board[start_r + direction][start_c]):
                return True
            if (player_color == 'white' and start_r == 6 and end_r == start_r + 2 * direction and start_c == end_c and not target_piece_info and not board[start_r + direction][start_c]):
                return True
            # Capture
            if abs(start_c - end_c) == 1 and end_r == start_r + direction and target_piece_info:
                return True
            return False

        elif piece_type == 'R': # Rook
            if start_r == end_r: # Horizontal
                step = 1 if end_c > start_c else -1
                for c in range(start_c + step, end_c, step):
                    if board[start_r][c]: return False
                return True
            elif start_c == end_c: # Vertical
                step = 1 if end_r > start_r else -1
                for r in range(start_r + step, end_r, step):
                    if board[r][start_c]: return False
                return True
            return False

        elif piece_type == 'N': # Knight
            dr = abs(start_r - end_r)
            dc = abs(start_c - end_c)
            return (dr == 2 and dc == 1) or (dr == 1 and dc == 2)

        elif piece_type == 'B': # Bishop
            if abs(start_r - end_r) == abs(start_c - end_c):
                # Check path for obstructions
                dr_step = 1 if end_r > start_r else -1
                dc_step = 1 if end_c > start_c else -1
                r, c = start_r + dr_step, start_c + dc_step
                while r != end_r:
                    if board[r][c]: return False
                    r += dr_step
                    c += dc_step
                return True
            return False

        elif piece_type == 'Q': # Queen
            # Queen combines Rook and Bishop moves
            if self._is_valid_move_rook_like_pattern(start_r, start_c, end_r, end_c, board) or \
               self._is_valid_move_bishop_like_pattern(start_r, start_c, end_r, end_c, board):
                return True
            return False

        elif piece_type == 'K': # King
            dr = abs(start_r - end_r)
            dc = abs(start_c - end_c)

            # Normal King move (one square in any direction)
            if dr <= 1 and dc <= 1:
                return True

            # Castling logic (only if `has_moved_state` is provided and relevant for this check)
            if dr == 0 and abs(dc) == 2 and has_moved_state is not None:
                # Determine kingside or queenside castling
                if end_c == start_c + 2: # Kingside castling
                    rook_col = 7
                    rook_key = f"{player_color}_rook_kingside"
                    path_clear_cols = [5, 6] # Squares between King and Rook
                elif end_c == start_c - 2: # Queenside castling
                    rook_col = 0
                    rook_key = f"{player_color}_rook_queenside"
                    path_clear_cols = [1, 2, 3] # Squares between King and Rook
                else:
                    return False # Not a valid castling horizontal move

                # Check if King and Rook haven't moved
                if has_moved_state[f"{player_color}_king"] or has_moved_state[rook_key]:
                    return False

                # Check if the rook is actually at the expected position
                rook_info = board[start_r][rook_col]
                if not rook_info or rook_info[0] != 'R' or rook_info[1] != player_color:
                    return False

                # Check if path between King and Rook is clear
                for c in path_clear_cols:
                    if board[start_r][c] is not None:
                        return False

                # For castling, also need to check if the king passes through or lands on an attacked square
                # This is a simplified check for now, full check requires `is_square_attacked`
                # For a full implementation, you'd check if (start_r, start_c), (start_r, start_c +/- 1), (start_r, end_c) are attacked
                return True
            return False # Not a normal king move and not a valid castling move

        return False # Default to invalid for unknown piece types or invalid moves

    def _is_valid_move_rook_like_pattern(self, start_r, start_c, end_r, end_c, board):
        """Helper for Queen/Rook: Checks if a move is valid along a straight line pattern."""
        if start_r == end_r: # Horizontal
            step = 1 if end_c > start_c else -1
            for c in range(start_c + step, end_c, step):
                if board[start_r][c]: return False
            return True
        elif start_c == end_c: # Vertical
            step = 1 if end_r > start_r else -1
            for r in range(start_r + step, end_r, step):
                if board[r][start_c]: return False
            return True
        return False

    def _is_valid_move_bishop_like_pattern(self, start_r, start_c, end_r, end_c, board):
        """Helper for Queen/Bishop: Checks if a move is valid along a diagonal line pattern."""
        if abs(start_r - end_r) == abs(start_c - end_c):
            dr_step = 1 if end_r > start_r else -1
            dc_step = 1 if end_c > start_c else -1
            r, c = start_r + dr_step, start_c + dc_step
            while r != end_r:
                if board[r][c]: return False
                r += dr_step
                c += dc_step
            return True
        return False

    def _find_king_position(self, player_color, board):
        """Finds the current position of the King for the given player."""
        for r in range(8):
            for c in range(8):
                piece_info = board[r][c]
                if piece_info and piece_info[0] == 'K' and piece_info[1] == player_color:
                    return (r, c)
        return None # Should not happen in a valid game state

    def is_in_check(self, player_color, board):
        """Checks if the given player's King is currently in check on the provided board."""
        king_r, king_c = self._find_king_position(player_color, board)
        if king_r is None: return False # King not found (should not happen)

        opponent_color = 'black' if player_color == 'white' else 'white'

        # Iterate through all squares to find opponent's pieces
        for r in range(8):
            for c in range(8):
                piece_info = board[r][c]
                if piece_info and piece_info[1] == opponent_color:
                    # Check if this opponent piece can attack the king's position
                    # Use _is_valid_move_pattern for this check, passing None for has_moved_state
                    # as castling rules are not relevant for attacking the king.
                    if self._is_valid_move_pattern(r, c, king_r, king_c, board, None):
                        return True # Opponent piece can attack the King
        return False

    def is_checkmate(self, player_color):
        """Checks if the given player is in checkmate."""
        if not self.is_in_check(player_color, self.board):
            return False # Not in check, so cannot be checkmate

        # Iterate through all pieces of the current player
        for start_r in range(8):
            for start_c in range(8):
                piece_info = self.board[start_r][start_c]
                if piece_info and piece_info[1] == player_color:
                    # For each piece, check all possible moves
                    for end_r in range(8):
                        for end_c in range(8):
                            # If a move is found that gets the king out of check, it's not checkmate
                            if self.is_valid_move(start_r, start_c, end_r, end_c):
                                return False # Found a legal move to escape check
        return True # No legal moves found, it's checkmate

    def is_stalemate(self, player_color):
        """Checks if the given player is in stalemate (not in check, but no legal moves)."""
        if self.is_in_check(player_color, self.board):
            return False # In check, so cannot be stalemate

        # Check if there are any legal moves for the current player
        for start_r in range(8):
            for start_c in range(8):
                piece_info = self.board[start_r][start_c]
                if piece_info and piece_info[1] == player_color:
                    for end_r in range(8):
                        for end_c in range(8):
                            if self.is_valid_move(start_r, start_c, end_r, end_c):
                                return False # Found a legal move, so not stalemate
        return True # No legal moves found, and not in check, so it's stalemate


# Main application setup
if __name__ == "__main__":
    root = tk.Tk()
    game = ChessGame(root)
    root.mainloop()
