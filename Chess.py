'''Chess by anay.taparia@gmail.com
The 8x8 game'''
import sys
WIDTH = 8
HEIGHT = 8
BLANK = ' '
WHITE = "white"
BLACK = "black"


class Piece:
    def __init__(self,kind,color):
        self.kind = kind
        self.color = color

    def __str__(self):
        return self.kind.upper() if self.color == WHITE else self.kind.lower()
    
    def get_unicode_str(self):
        str_to_unicode_W = {"K":"♚","Q":"♛","R":"♜","B":"♝","N":"♞","P":"♟"}
        str_to_unicode_B = {"K":"♔","Q":"♕","R":"♖","B":"♗","N":"♘","P":"♙"}
        if self.color == WHITE:
            return str_to_unicode_W[self.kind]
        if self.color == BLACK:
            return str_to_unicode_B[self.kind]
    
class Board:
    def __init__(self,turn=WHITE):
        self.board = self.new_board()
        self.turn = turn
        #useful for special moves later on
        self.wks = True
        self.wqs = True
        self.bks = True
        self.bqs = True
        self.enpass = False

    def new_board(self):
        return [[Piece('R',WHITE),Piece('N',WHITE),Piece('B',WHITE),Piece('Q',WHITE),Piece('K',WHITE),Piece('B',WHITE),Piece('N',WHITE),Piece('R',WHITE)],
                [Piece('P',WHITE),Piece('P',WHITE),Piece('P',WHITE),Piece('P',WHITE),Piece('P',WHITE),Piece('P',WHITE),Piece('P',WHITE),Piece('P',WHITE)],
                [None,None,None,None,None,None,None,None],
                [None,None,None,None,None,None,None,None],
                [None,None,None,None,None,None,None,None],
                [None,None,None,None,None,None,None,None],
                [Piece('P',BLACK),Piece('P',BLACK),Piece('P',BLACK),Piece('P',BLACK),Piece('P',BLACK),Piece('P',BLACK),Piece('P',BLACK),Piece('P',BLACK)],
                [Piece('R',BLACK),Piece('N',BLACK),Piece('B',BLACK),Piece('Q',BLACK),Piece('K',BLACK),Piece('B',BLACK),Piece('N',BLACK),Piece('R',BLACK)],]

    def print_board(self):
        rowsep='  +---+---+---+---+---+---+---+---+'
        print('    a   b   c   d   e   f   g   h')
        print(rowsep)
        for y,rank in enumerate(self.board):
            print(y+1,"|",end="")
            for x,square in enumerate(rank):
                if self.board[7-y][x] is None:
                    print(BLANK*3,end="|")
                else:
                    print(f" {self.board[7-y][x]} ",end="|")
            print()
            print(rowsep)
    
class Move:
    def __init__(self,stri):
        self.sf=ord(stri[0])-ord("a")
        self.sr=int(stri[1])-1
        self.ef=ord(stri[2])-ord("a")
        self.er=int(stri[3])-1

    def unpck(self):
        return (self.sf,self.sr,self.ef,self.er)
    
class Game:
    def __init__(self):
        self.board = Board() 

    def get_input(self):
        while True:
            move = input("enter your move or 'quit'\n> ")
            if move == 'quit':
                sys.exit()
            try:
                move = Move(move)
                break
            except:
                print("invalid move")
                continue
        return move
    
    def is_move_legal(self, move):
        board = self.board.board
        sf,sr,ef,er = move.unpck()
        target = board[er][ef]        
        capture = not (target==None)
        piece = board[sr][sf]
        dr = sr-er
        df = sf-ef
        if target.color == piece.color:
            return False # pieces cannot capture pieces of their own color
        
        elif piece.kind == "N": # added knight logic only
            if (abs(dr),abs(df)) in [(2,1),(1,2)]:
                return True
            else:
                return False
        elif piece.kind == "P":
            if piece.color == WHITE:
                if target: # capture
                    if (dr,df) in [(1,1),(1,-1)]:
                        return True
                    else:
                        return False
                else: # not capture
                    if (dr,df) == (1,0) or (er-1,ef) == Piece("P",BLACK): # the second condition of the OR adds legal move detection for en passant.
                        return True
                    else:
                        return False
            if piece.color == BLACK:
                if target: # capture
                    if (dr,df) in [(-1,1),(-1,-1)]:
                        return True
                    else:
                        return False
                else: # not capture
                    if (dr,df) == (-1,0) or (er+1,ef) == Piece("P",WHITE): # the second condition of the OR adds legal move detection for en passant.
                        return True
                    else:
                        return False
        return True # everything else is legal
    
    def give_sliding_moves(self, dr, df, sr, sf):
        '''Gives a list of sliding moves from sx,sy in direction dx,dy until blocked'''
        bord = self.board.board
        moves = []
        moves.append((sr,sf))
        colr = bord[sf][sr].color
        target = bord[sf][sr]
        while target == None or target.color != colr:
            sr,sf = sr+dr,sf+df
            moves.append((sr,sf))
            target = bord[sf][sr]
        return moves

    def make_move(self,move):
        sf,sr,ef,er = move.unpck()
        capture = not self.board.board[er][ef]
        
        if self.board.board[sr][sf].kind == 'P': # Promotion
            if self.board.board[sr][sf].color == WHITE and er == 7:
                self.board.board[er][ef]=Piece(input("enter promotion piece in upcase\n> "),WHITE)
                self.board.board[sr][sf]=None
                return None
            elif self.board.board[sr][sf].color == BLACK and er == 0:
                self.board.board[er][ef]=Piece(input("enter promotion piece in upcase\n> "),BLACK)
                self.board.board[sr][sf]=None
                return None
                

        if self.board.board[sr][sf].kind == 'K': # remove castling rights
            if self.board.board[sr][sf].color == WHITE:
                self.board.wks = False
                self.board.wqs = False
            elif self.board.board[sr][sf].color == BLACK:
                self.board.bks = False
                self.board.bqs = False
        # i wont add rook castle logic yet
        if self.board.board[sr][sf].kind == 'P': # Using logic for en passant
            # so it is if the pawn moves to an EMPTY square. delete the square behind it.
            # if the move is normal. pawns move would get blocked if there was  a piece.
            # and with a capture. it is not an empty square
            if self.board.board[sr][sf].color == WHITE and not capture:
                self.board.board[er][ef]=self.board.board[sr][sf]
                self.board.board[er-1][ef]=None
                self.board.board[sr][sf]=None
                return None
            elif self.board.board[sr][sf].color == BLACK and not capture:
                self.board.board[er][ef]=self.board.board[sr][sf]
                self.board.board[er+1][ef]=None
                self.board.board[sr][sf]=None
                return None

        self.board.board[er][ef]=self.board.board[sr][sf]
        self.board.board[sr][sf]=None
        return None
    
    def main(self):
        while True:
            self.board.print_board()
            move = self.get_input()
            if self.is_move_legal(move):
                self.make_move(move)

if __name__ == "__main__":
    chess = Game()
    chess.main()       

