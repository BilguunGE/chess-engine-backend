import math
import re
import numpy as np


def makeField(row, col):
    colNames = ["a", "b", "c", "d", "e", "f", "g", "h"]
    rowNames = ["8", "7", "6", "5", "4", "3", "2", "1"]
    return colNames[col] + rowNames[row]


class Board:
    ZERO_STRING = "0000000000000000000000000000000000000000000000000000000000000000"
    ONE = np.uint64(1)
    TWO = np.uint64(2)
    FILE_A=np.uint64(72340172838076673)
    FILE_H=np.uint64(-9187201950435737472)
    FILE_AB=np.uint(217020518514230019)
    FILE_GH=np.uint(-4557430888798830400)
    RANK_1=np.uint64(-72057594037927936)
    RANK_4=np.uint64(1095216660480)
    RANK_5=np.uint64(4278190080)
    RANK_8=np.uint64(255)

    RankMasks8 = {'1': np.uint64(0xFF), '2': np.uint64(0xFF00), '3': np.uint64(0xFF0000), '4': np.uint64(0xFF000000), '5': np.uint64(
        0xFF00000000), '6': np.uint64(0xFF0000000000), '7': np.uint(0xFF000000000000), '8': np.uint64(0xFF00000000000000)}
    FileMasks8 = {
        'a': np.uint64(0x101010101010101), 'b': np.uint64(0x202020202020202), 'c': np.uint64(0x404040404040404), 'd': np.uint64(0x808080808080808),
        'e': np.uint64(0x1010101010101010), 'f': np.uint64(0x2020202020202020), 'g': np.uint64(0x4040404040404040), 'h': np.uint64(0x8080808080808080)}
    
    DiagonalMasks8 = [
	np.uint64(0x1), np.uint64(0x102), np.uint64(0x10204), np.uint64(0x1020408), np.uint64(
	    0x102040810), np.uint64(0x10204081020), np.uint64(0x1020408102040),
	np.uint64(0x102040810204080), np.uint64(0x204081020408000), np.uint64(
	    0x408102040800000), np.uint64(0x810204080000000),
	np.uint64(0x1020408000000000), np.uint64(0x2040800000000000), np.uint64(
	    0x4080000000000000), np.uint64(0x8000000000000000)
    ]
    
    AntiDiagonalMasks8 = [
	np.uint64(0x80), np.uint64(0x8040), np.uint64(0x804020), np.uint64(0x80402010), np.uint64(
	    0x8040201008), np.uint64(0x804020100804), np.uint64(0x80402010080402),
	np.uint64(0x8040201008040201), np.uint64(0x4020100804020100), np.uint64(
	    0x2010080402010000), np.uint64(0x1008040201000000),
	np.uint64(0x804020100000000), np.uint64(0x402010000000000), np.uint64(
	    0x201000000000000), np.uint64(0x100000000000000)
    ]
        
    WP = np.uint64(0)
    WN = np.uint64(0)
    WB = np.uint64(0)
    WR = np.uint64(0)
    WQ = np.uint64(0)
    WK = np.uint64(0)
    BP = np.uint64(0)
    BN = np.uint64(0)
    BB = np.uint64(0)
    BR = np.uint64(0)
    BQ = np.uint64(0)
    BK = np.uint64(0)
    

    NOT_WHITE_PIECES = np.uint64(0)
    BLACK_PIECES = np.uint64(0)
    EMPTY = np.uint64(0)
    OCCUPIED = np.uint64(0)


    isWhiteTurn = True
    castleRight = "KQkq"
    enPassant = "-"
    halfmoveClock = 0
    fullmoveCount = 1
    chessBoard = [
        ["r", "n", "b", "q", "k", "b", "n", "r"],
        ["p", "p", "p", "p", "p", "p", "p", "p"],
        ["", "", "", "", "", "", "", ""],
        ["", "", "", "", "", "", "", ""],
        ["", "", "", "", "", "", "", ""],
        ["", "", "", "", "", "", "", ""],
        ["P", "P", "P", "P", "P", "P", "P", "P"],
        ["R", "N", "B", "Q", "K", "B", "N", "R"],
    ]

    def __init__(self, fenString=None):
        self.fenString = fenString
        self.initBoard()
        self.convertArraysToBitboards()

    def initBoard(self):
        if not self.fenString is None:
            splittedFEN = self.fenString.split(' ')
            self.chessBoard = self.parseFEN(splittedFEN[0])
            self.isWhiteTurn = splittedFEN[1] == "w"
            self.castleRight = splittedFEN[2]
            self.enPassant = splittedFEN[3]
            self.halfmoveClock = int(splittedFEN[4])
            self.fullmoveCount = int(splittedFEN[5])

    def parseFEN(self, boardString):
        board = []
        rows = boardString.split("/")
        for row in rows:
            rowContent = []
            for cell in row:
                if re.match('\d', cell):
                    for n in range(int(cell)):
                        rowContent.append("")
                else:
                    rowContent.append(cell)
            board.append(rowContent)
        return board

    def convertArraysToBitboards(self):
        for i in range(64):
            binary = self.ZERO_STRING[i+1:] + "1" + self.ZERO_STRING[0:i]
            num = np.uint64(int(binary, 2))
            row = (i // 8)
            col = i % 8
            figure = self.chessBoard[row][col]
            if figure == "P":
                self.WP += num
            elif figure == "N":
                self.WN += num
            elif figure == "B":
                self.WB += num
            elif figure == "R":
                self.WR += num
            elif figure == "Q":
              self.WQ += num
            elif figure == "K":
              self.WK += num
            elif figure == "p":
              self.BP += num
            elif figure == "n":
              self.BN += num
            elif figure == "b":
              self.BB += num
            elif figure == "r":
              self.BR += num
            elif figure == "q":
              self.BQ += num
            elif figure == "k":
              self.BK += num

    def convertBitboardsToArray(self):
        newChessBoard = []
        for rowI in range(8):
            cellContent = []
            for cellJ in range(8):
                cellContent.append('')
            newChessBoard.append(cellContent)

        for i in range(64):
            row = (i // 8)
            col = i % 8
            if (self.WP >> np.uint64(i)) & self.ONE == self.ONE:
                newChessBoard[row][col] = "P"
            if (self.WN >> np.uint64(i)) & self.ONE == self.ONE:
                newChessBoard[row][col] = "N"
            if (self.WB >> np.uint64(i)) & self.ONE == self.ONE:
                newChessBoard[row][col] = "B"
            if (self.WR >> np.uint64(i)) & self.ONE == self.ONE:
                newChessBoard[row][col] = "R"
            if (self.WQ >> np.uint64(i)) & self.ONE == self.ONE:
                newChessBoard[row][col] = "Q"
            if (self.WK >> np.uint64(i)) & self.ONE == self.ONE:
                newChessBoard[row][col] = "K"
            if (self.BP >> np.uint64(i)) & self.ONE == self.ONE:
                newChessBoard[row][col] = "p"
            if (self.BN >> np.uint64(i)) & self.ONE == self.ONE:
                newChessBoard[row][col] = "n"
            if (self.BB >> np.uint64(i)) & self.ONE == self.ONE:
                newChessBoard[row][col] = "b"
            if (self.BR >> np.uint64(i)) & self.ONE == self.ONE:
                newChessBoard[row][col] = "r"
            if (self.BQ >> np.uint64(i)) & self.ONE == self.ONE:
                newChessBoard[row][col] = "q"
            if (self.BK >> np.uint64(i)) & self.ONE == self.ONE:
                newChessBoard[row][col] = "k"

        return newChessBoard

    def getMoves(self):
        # exluding black king, because he can't be eaten
        self.BLACK_PIECES = self.BP | self.BN | self.BB | self.BR | self.BQ

        # same here
        self.WHITE_PIECES = self.WP | self.WN | self.WB | self.WR | self.WQ

        self.OCCUPIED = self.WP | self.WN | self.WB | self.WR | self.WQ | self.WK | self.BP | self.BN | self.BB | self.BR | self.BQ | self.BK

        # board with empty fields
        self.EMPTY= ~self.OCCUPIED

        return self.getMovesP()

    def getMovesP(self):
        moves = []
        color = 1
        if not self.isWhiteTurn:
            color = -1

        # beat right
        PAWN_MOVES = (self.WP >> np.uint64(7)) & self.BLACK_PIECES & ~self.RANK_8 & ~ self.FILE_A
        PAWN_MOVES_PROMO = (self.WP >> np.uint64(7)) & self.BLACK_PIECES & self.RANK_8 & ~self.FILE_A

        if not self.isWhiteTurn:
            PAWN_MOVES = (self.BP << np.uint64(7)) & self.WHITE_PIECES & ~self.RANK_1 & ~ self.FILE_H
            PAWN_MOVES_PROMO = (self.BP << np.uint64(7)) & self.WHITE_PIECES & self.RANK_1 & ~self.FILE_H

        for i in range(64):
            move = {}
            if (PAWN_MOVES_PROMO >> np.uint64(i)) & self.ONE == self.ONE:
                move['isPromo'] = True
            if (PAWN_MOVES >> np.uint64(i)) & self.ONE  == self.ONE :
                move['toString'] = makeField((i//8)+(color*1), (i % 8)-(color*1)) + "x" + makeField((i//8), i % 8)
                move['isHit'] = True
                moves.append(move)

        # beat left
        PAWN_MOVES = (self.WP >> np.uint64(9)) & self.BLACK_PIECES & ~self.RANK_8 & ~ self.FILE_H
        PAWN_MOVES_PROMO = (self.WP >> np.uint64(9)) & self.BLACK_PIECES & self.RANK_8 & ~self.FILE_H

        if not self.isWhiteTurn:
            PAWN_MOVES = (self.BP << np.uint64(9)) & self.WHITE_PIECES & ~self.RANK_1 & ~ self.FILE_A
            PAWN_MOVES_PROMO = (self.BP << np.uint64(9)) & self.WHITE_PIECES & self.RANK_1 & ~self.FILE_A

        for i in range(64):
            move = {}
            if (PAWN_MOVES_PROMO >> np.uint64(i)) & self.ONE == self.ONE:
                move['isPromo'] = True
            if (PAWN_MOVES >> np.uint64(i)) & self.ONE == self.ONE:
                move['toString'] = makeField((i//8)+(color*1), (i % 8)-(color*1)) + "x"+makeField((i//8), i % 8)
                move['isHit'] = True
                moves.append(move)

        # move 1 forward
        PAWN_MOVES = (self.WP >> np.uint64(8)) & self.EMPTY & ~self.RANK_8
        PAWN_MOVES_PROMO = (self.WP >> np.uint64(8)) & self.EMPTY & self.RANK_8

        if not self.isWhiteTurn:
            PAWN_MOVES = (self.BP << np.uint64(8)) & self.EMPTY & ~self.RANK_1
            PAWN_MOVES_PROMO = (self.BP << np.uint64(8)) & self.EMPTY & self.RANK_1

        for i in range(64):
            move = {}
            if (PAWN_MOVES_PROMO >> np.uint64(i)) & self.ONE == self.ONE:
                move['isPromo'] = True
            if (PAWN_MOVES >> np.uint64(i)) & self.ONE == self.ONE:
                move['toString'] = makeField((i//8)+(color*1), (i % 8)) + "-"+makeField((i//8), i % 8)
                move['isHit'] = False
                moves.append(move)

        # move 2 forward
        PAWN_MOVES = (self.WP >> np.uint64(16)) & self.EMPTY & (self.EMPTY >> np.uint64(8)) & self.RANK_4
    
        if not self.isWhiteTurn:
            PAWN_MOVES = (self.BP << np.uint64(16)) & self.EMPTY & (self.EMPTY << np.uint64(8)) & self.RANK_5

        for i in range(64):
            move = {}
            if (PAWN_MOVES >> np.uint64(i)) & self.ONE == self.ONE:
                move['toString'] = makeField((i//8)+(color*2), (i % 8)) + "-"+makeField((i//8), i % 8)
                move['isHit'] = False
                moves.append(move)

        if self.enPassant != '-':
            RANK = self.FileMasks8[self.enPassant[0]]

            # en passant right
            PAWN_MOVES = (self.WP << self.ONE) & self.BP & self.RANK_5 & ~self.FILE_A & RANK
            
            if not self.isWhiteTurn:
                PAWN_MOVES = (self.BP >> self.ONE) & self.WP & self.RANK_4 & ~self.FILE_H & RANK
            
            for i in range(64):
                move = {}
                if (PAWN_MOVES >> np.uint64(i)) & self.ONE == self.ONE:
                    move['toString'] = makeField((i//8), i % 8-(color*1))+'x'+self.enPassant
                    move['isHit'] = True
                    move['enPassant'] = True
                    moves.append(move)

            # en passant left
            PAWN_MOVES = (self.WP >> self.ONE) & self.BP & self.RANK_5 & ~self.FILE_H & RANK

            if not self.isWhiteTurn:
                PAWN_MOVES = (self.BP << self.ONE) & self.WP & self.RANK_4 & ~self.FILE_A & RANK

            for i in range(64):
                move = {}
                if (PAWN_MOVES >> np.uint64(i)) & self.ONE == self.ONE:
                    move['toString'] = makeField((i//8), i % 8+(color*1))+'x'+self.enPassant
                    move['isHit'] = True
                    move['enPassant'] = True
                    moves.append(move)

        return moves

    def HAndVMoves(self, s:np.uint64):
        binaryS = np.uint64(1 << s)
        possibilitiesHorizontal = (self.OCCUPIED - self.TWO * binaryS) ^ np.invert(np.invert(self.OCCUPIED) - self.TWO * np.invert(binaryS))
        possibilitiesVertical = ((self.OCCUPIED & self.FileMasks8[s % 8]) - (self.TWO * binaryS)) ^ np.invert(np.invert(self.OCCUPIED & self.FileMasks8[s % 8]) - (self.TWO * np.invert(binaryS)))
        return (possibilitiesHorizontal & self.RankMasks8[(s // 8)]) | (possibilitiesVertical & self.FileMasks8[s % 8])
    
    def DAndAntiDMoves(self, s:np.uint64):
        binaryS = np.uint64(1 << s)
        possibilitiesDiagonal = ((self.OCCUPIED & self.DiagonalMasks8[(s // 8) + (s % 8)]) - (self.TWO * binaryS)) ^ np.invert(np.invert(self.OCCUPIED & self.DiagonalMasks8[(s // 8) + (s % 8)]) - (self.TWO * np.invert(binaryS)))
        possibilitiesAntiDiagonal = ((self.OCCUPIED & self.AntiDiagonalMasks8[(s // 8) + 7 - (s % 8)]) - (self.TWO * binaryS)) ^ np.invert(np.invert(self.OCCUPIED & self.AntiDiagonalMasks8[(s // 8) + 7 - (s % 8)]) - (self.TWO * np.invert(binaryS)))
        return (possibilitiesDiagonal & self.DiagonalMasks8[(s // 8) + (s % 8)]) | (possibilitiesAntiDiagonal & self.AntiDiagonalMasks8[(s // 8) + 7 - (s % 8)])
    
b = Board('rnbqkbnr/pppppppp/8/8/8/8/PPPPPPPP/RNBQKBNR w KQkq - 0 1')
print((b.getMoves()))
print(np.binary_repr(b.WP))