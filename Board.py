import math
import re


def makeField(row, col):
    colNames = ["a", "b", "c", "d", "e", "f", "g", "h"]
    rowNames = ["8", "7", "6", "5", "4", "3", "2", "1"]
    return colNames[col] + rowNames[row]


class Board:
    ZERO_STRING = "0000000000000000000000000000000000000000000000000000000000000000"

    RANK_1 = int(
        "1111111100000000000000000000000000000000000000000000000000000000", 2)

    RANK_2 = int(
        "0000000011111111000000000000000000000000000000000000000000000000", 2)
    RANK_3 = int(
        "0000000000000000111111110000000000000000000000000000000000000000", 2)
    RANK_4 = int(
        "0000000000000000000000001111111100000000000000000000000000000000", 2)
    RANK_5 = int(
        "0000000000000000000000000000000011111111000000000000000000000000", 2)
    RANK_6 = int(
        "0000000000000000000000000000000000000000111111110000000000000000", 2)
    RANK_7 = int(
        "0000000000000000000000000000000000000000000000001111111100000000", 2)
    RANK_8 = int(
        "0000000000000000000000000000000000000000000000000000000011111111", 2)
    RANK_H = int(
        "1000000010000000100000001000000010000000100000001000000010000000", 2)
    RANK_G = int(
        "0100000001000000010000000100000001000000010000000100000001000000", 2)
    RANK_F = int(
        "0010000000100000001000000010000000100000001000000010000000100000", 2)
    RANK_E = int(
        "0001000000010000000100000001000000010000000100000001000000010000", 2)
    RANK_D = int(
        "0000100000001000000010000000100000001000000010000000100000001000", 2)
    RANK_C = int(
        "0000010000000100000001000000010000000100000001000000010000000100", 2)
    RANK_B = int(
        "0000001000000010000000100000001000000010000000100000001000000010", 2)
    RANK_A = int(
        "0000000100000001000000010000000100000001000000010000000100000001", 2)
    RANK_MAP = {
        'a': RANK_A,
        'b': RANK_B,
        'c': RANK_C,
        'd': RANK_D,
        'e': RANK_E,
        'f': RANK_F,
        'g': RANK_G,
        'h': RANK_H
    }
    WP = 0
    WN = 0
    WB = 0
    WR = 0
    WQ = 0
    WK = 0
    BP = 0
    BN = 0
    BB = 0
    BR = 0
    BQ = 0
    BK = 0

    NOT_WHITE_PIECES = 0
    BLACK_PIECES = 0
    EMPTY = 0

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
            num = int(binary, 2)
            row = math.floor(i / 8)
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
            row = math.floor(i / 8)
            col = i % 8
            if (self.WP >> i) & 1 == 1:
                newChessBoard[row][col] = "P"
            if (self.WN >> i) & 1 == 1:
                newChessBoard[row][col] = "N"
            if (self.WB >> i) & 1 == 1:
                newChessBoard[row][col] = "B"
            if (self.WR >> i) & 1 == 1:
                newChessBoard[row][col] = "R"
            if (self.WQ >> i) & 1 == 1:
                newChessBoard[row][col] = "Q"
            if (self.WK >> i) & 1 == 1:
                newChessBoard[row][col] = "K"
            if (self.BP >> i) & 1 == 1:
                newChessBoard[row][col] = "p"
            if (self.BN >> i) & 1 == 1:
                newChessBoard[row][col] = "n"
            if (self.BB >> i) & 1 == 1:
                newChessBoard[row][col] = "b"
            if (self.BR >> i) & 1 == 1:
                newChessBoard[row][col] = "r"
            if (self.BQ >> i) & 1 == 1:
                newChessBoard[row][col] = "q"
            if (self.BK >> i) & 1 == 1:
                newChessBoard[row][col] = "k"

        return newChessBoard

    def getMovesW(self):
        # including black king, because he can't be eaten
        self.NOT_WHITE_PIECES = ~(
            self.WP | self.WN | self.WB | self.WR | self.WQ | self.WK | self.BK)

        # same here
        self.BLACK_PIECES = self.BP | self.BN | self.BB | self.BR | self.BQ

        # board with empty fields
        self.EMPTY = ~(self.WP | self.WN | self.WB | self.WR | self.WQ |
                       self.WK | self.BP | self.BN | self.BB | self.BR | self.BQ | self.BK)
        return self.getMovesWP()

    def getMovesWP(self):
        moves = []

        # beat left
        PAWN_MOVES = (
            self.WP >> 7) & self.BLACK_PIECES & ~self.RANK_1 & ~ self.RANK_A

        PAWN_MOVES_PROMO = (
            self.WP >> 7) & self.BLACK_PIECES & self.RANK_8 & ~self.RANK_A

        for i in range(64):
            move = {}
            if (PAWN_MOVES_PROMO >> i) & 1 == 1:
                move['isPromo'] = True
            if (PAWN_MOVES >> i) & 1 == 1:
                move['toString'] = makeField(math.floor(
                    i/8)+1, (i % 8)-1) + "x" + makeField(math.floor(i/8), i % 8)
                move['isHit'] = True
                moves.append(move)

        # beat right
        PAWN_MOVES = (
            self.WP >> 9) & self.BLACK_PIECES & ~self.RANK_1 & ~ self.RANK_H

        PAWN_MOVES_PROMO = (
            self.WP >> 9) & self.BLACK_PIECES & self.RANK_8 & ~self.RANK_H

        for i in range(64):
            move = {}
            if (PAWN_MOVES_PROMO >> i) & 1 == 1:
                move['isPromo'] = True
            if (PAWN_MOVES >> i) & 1 == 1:
                move['toString'] = makeField(math.floor(
                    i/8)+1, (i % 8)-1) + "x"+makeField(math.floor(i/8), i % 8)
                move['isHit'] = True
                moves.append(move)

        # move 1 forward
        PAWN_MOVES = (self.WP >> 8) & self.EMPTY & ~self.RANK_1
        PAWN_MOVES_PROMO = (self.WP >> 8) & self.EMPTY & self.RANK_8
        print(format(self.WP, 'b'), "??")

        for i in range(64):
            move = {}
            if (PAWN_MOVES_PROMO >> i) & 1 == 1:
                move['isPromo'] = True
            if (PAWN_MOVES >> i) & 1 == 1:
                move['toString'] = makeField(math.floor(
                    i/8)+1, (i % 8)) + "-"+makeField(math.floor(i/8), i % 8)
                move['isHit'] = False
                moves.append(move)

        # move 2 forward
        PAWN_MOVES = (self.WP >> 16) & self.EMPTY & (
            self.EMPTY >> 8) & self.RANK_4
        for i in range(64):
            move = {}
            if (PAWN_MOVES >> i) & 1 == 1:
                move['toString'] = makeField(math.floor(
                    i/8)+2, (i % 8)) + "-"+makeField(math.floor(i/8), i % 8)
                move['isHit'] = False
                moves.append(move)

        if self.enPassant != '-':
            RANK = self.RANK_MAP[self.enPassant[0]]

            # en passant left
            PAWN_MOVES = (
                self.WP << 1) & self.BP & self.RANK_5 & ~self.RANK_A & RANK

            for i in range(64):
                move = {}

                if PAWN_MOVES >> i == 1:
                    move['toString'] = makeField(
                        math.floor(i/8), i % 8-1)+'x'+self.enPassant
                    move['isHit'] = True
                    move['enPassant'] = True
                    moves.append(move)

            # en passant right
            PAWN_MOVES = (
                self.WP >> 1) & self.BP & self.RANK_5 & ~self.RANK_H & RANK
            for i in range(64):
                move = {}
                if PAWN_MOVES >> i == 1:
                    move['toString'] = makeField(
                        math.floor(i/8), i % 8+1)+'x'+self.enPassant
                    move['isHit'] = True
                    move['enPassant'] = True
                    moves.append(move)

        return moves
