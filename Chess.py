'''Chess by anay.taparia@gmail.com
The 8x8 game'''
import sys
WIDTH = 8
HEIGHT = 8
BLANK = ''
WHITE = "white"
BLACK = "black"


class Piece:
    def __init__(self,kind,color):
        self.kind = kind
        self.color = color

    def __str__(self):
        return self.kind.upper() if self.color == WHITE else self.kind.lower()
    
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
        rowsep=' +-+-+-+-+-+-+-+-+'
        print('  a b c d e f g h')
        print(rowsep)
        for y,rank in enumerate(self.board):
            print(y+1,"|",end="")
            for x,square in enumerate(rank):
                print(square,end="|")
                print(rowsep)
    
class Move:
    def __init__(self,stri):
        self.sf=ord(stri[0])-ord("a")
        self.sr=int(stri[1]-1)
        self.ef=ord(stri[2])-ord("a")
        self.er=int(stri[3]-1)

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
    
    def make_move(self,move):
        sf,sr,ef,er = move.unpck()
        if self.board[sr][sf].kind == 'K': # remove castling rights
            if self.board[sr][sf].color == "white":
                self.board.wks = False
                self.board.wqs = False
            elif self.board[sr][sf].color == "black":
                self.board.bks = False
                self.board.bqs = False
        # i wont add rook castle logic yet

        self.board[er][ef]=self.board[sr][sf]
        self.board[sr][sf]=None
    
    def main(self):
        while True:
            self.board.print_board()
            self.make_move(self.get_input())

if __name__ == "__main__":
    chess = Game
    chess.main()       
