import re
import numpy as np
from helpers import *


class Board:
    ZERO_STRING = "0000000000000000000000000000000000000000000000000000000000000000"
    FILE_A=np.uint64(72340172838076673)
    FILE_H=np.uint64(-9187201950435737472)
    FILE_AB=np.uint64(217020518514230019)
    FILE_GH=np.uint64(-4557430888798830400)
    RANK_1=np.uint64(-72057594037927936)
    RANK_4=np.uint64(1095216660480)
    RANK_5=np.uint64(4278190080)
    RANK_8=np.uint64(255)
    

    KNIGHT_SPAN = np.uint64(43234889994)
    # KNIGHT_SPAN = strBBtoBB("""
    #     00000000
    #     00000000
    #     00000000
    #     00001010
    #     00010001
    #     00000000
    #     00010001
    #     00001010
    # """)

    RankMasks8 = [np.uint64(0xFF),np.uint64(0xFF00), np.uint64(0xFF0000), np.uint64(0xFF000000), np.uint64(
        0xFF00000000), np.uint64(0xFF0000000000), np.uint64(0xFF000000000000), np.uint64(0xFF00000000000000)]

    FileMasks8 = {
        'a': np.uint64(0x101010101010101), 'b': np.uint64(0x202020202020202), 'c': np.uint64(0x404040404040404), 'd': np.uint64(0x808080808080808),
        'e': np.uint64(0x1010101010101010), 'f': np.uint64(0x2020202020202020), 'g': np.uint64(0x4040404040404040), 'h': np.uint64(0x8080808080808080)}
    
    FileMasks82 = [
         np.uint64(0x101010101010101),  np.uint64(0x202020202020202), np.uint64(0x404040404040404), np.uint64(0x808080808080808),
         np.uint64(0x1010101010101010),  np.uint64(0x2020202020202020),  np.uint64(0x4040404040404040),np.uint64(0x8080808080808080)]
    
    DiagonalMasks8 = [np.uint64(0x1), np.uint64(0x102), np.uint64(0x10204), np.uint64(0x1020408), np.uint64(0x102040810), np.uint64(0x10204081020), np.uint64(0x1020408102040),np.uint64(0x102040810204080), np.uint64(0x204081020408000), np.uint64(0x408102040800000), np.uint64(0x810204080000000),np.uint64(0x1020408000000000), np.uint64(0x2040800000000000), np.uint64(0x4080000000000000), np.uint64(0x8000000000000000)]
    
    AntiDiagonalMasks8 = [np.uint64(0x80), np.uint64(0x8040), np.uint64(0x804020), np.uint64(0x80402010), np.uint64(0x8040201008), np.uint64(0x804020100804), np.uint64(0x80402010080402),np.uint64(0x8040201008040201), np.uint64(0x4020100804020100), np.uint64(0x2010080402010000), np.uint64(0x1008040201000000),np.uint64(0x804020100000000), np.uint64(0x402010000000000), np.uint64(0x201000000000000), np.uint64(0x100000000000000)]
        
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
    

    BLACK_PIECES = np.uint64(0)
    WHITE_PIECES = np.uint64(0)

    MY_PIECES = np.uint64(0)
    NOT_MY_PIECES =  np.uint64(0)

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
            if (self.WP >> np.uint64(i)) & ONE == ONE:
                newChessBoard[row][col] = "P"
            if (self.WN >> np.uint64(i)) & ONE == ONE:
                newChessBoard[row][col] = "N"
            if (self.WB >> np.uint64(i)) & ONE == ONE:
                newChessBoard[row][col] = "B"
            if (self.WR >> np.uint64(i)) & ONE == ONE:
                newChessBoard[row][col] = "R"
            if (self.WQ >> np.uint64(i)) & ONE == ONE:
                newChessBoard[row][col] = "Q"
            if (self.WK >> np.uint64(i)) & ONE == ONE:
                newChessBoard[row][col] = "K"
            if (self.BP >> np.uint64(i)) & ONE == ONE:
                newChessBoard[row][col] = "p"
            if (self.BN >> np.uint64(i)) & ONE == ONE:
                newChessBoard[row][col] = "n"
            if (self.BB >> np.uint64(i)) & ONE == ONE:
                newChessBoard[row][col] = "b"
            if (self.BR >> np.uint64(i)) & ONE == ONE:
                newChessBoard[row][col] = "r"
            if (self.BQ >> np.uint64(i)) & ONE == ONE:
                newChessBoard[row][col] = "q"
            if (self.BK >> np.uint64(i)) & ONE == ONE:
                newChessBoard[row][col] = "k"

        return newChessBoard

    def getMoves(self):
        if self.isWhiteTurn:
            return  self.possibleMovesW()
        else:
            return self.possibleMovesB()

    def possibleMovesW(self):
        #added BK to avoid illegal capture
        self.NOT_MY_PIECES = ~(self.WP|self.WN|self.WB|self.WR|self.WQ|self.WK|self.BK)
        #omitted WK to avoid illegal capture
        self.MY_PIECES = self.WP|self.WN|self.WB|self.WR|self.WQ
        self.OCCUPIED=self.WP|self.WN|self.WB|self.WR|self.WQ|self.WK|self.BP|self.BN|self.BB|self.BR|self.BQ|self.BK
        self.EMPTY=~self.OCCUPIED
        return self.getMovesP()+self.getMovesB(self.WB)+self.getMovesN(self.WN)+self.getMovesQ(self.WQ)+self.getMovesR(self.WR)

        
    
    def possibleMovesB(self) :
        #added WK to avoid illegal capture
        self.NOT_MY_PIECES=~(self.BP|self.BN|self.BB|self.BR|self.BQ|self.BK|self.WK)
        #omitted BK to avoid illegal capture
        self.MY_PIECES=self.BP|self.BN|self.BB|self.BR|self.BQ
        self.OCCUPIED=self.WP|self.WN|self.WB|self.WR|self.WQ|self.WK|self.BP|self.BN|self.BB|self.BR|self.BQ|self.BK
        self.EMPTY=~self.OCCUPIED

        return self.getMovesP()+self.getMovesB(self.BB)+self.getMovesN(self.BN)+self.getMovesQ(self.BQ)+self.getMovesR(self.BR)
    
    def getMovesP(self):
        # exluding black king, because he can't be eaten
        self.BLACK_PIECES = self.BP | self.BN | self.BB | self.BR | self.BQ
        
        # same here
        self.WHITE_PIECES = self.WP | self.WN | self.WB | self.WR | self.WQ

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
            if (PAWN_MOVES_PROMO >> np.uint64(i)) & ONE == ONE:
                move['isPromo'] = True
            if (PAWN_MOVES >> np.uint64(i)) & ONE  == ONE :
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
            if (PAWN_MOVES_PROMO >> np.uint64(i)) & ONE == ONE:
                move['isPromo'] = True
            if (PAWN_MOVES >> np.uint64(i)) & ONE == ONE:
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
            if (PAWN_MOVES_PROMO >> np.uint64(i)) & ONE == ONE:
                move['isPromo'] = True
            if (PAWN_MOVES >> np.uint64(i)) & ONE == ONE:
                move['toString'] = makeField((i//8)+(color*1), (i % 8)) + "-"+makeField((i//8), i % 8)
                move['isHit'] = False
                moves.append(move)

        # move 2 forward
        PAWN_MOVES = (self.WP >> np.uint64(16)) & self.EMPTY & (self.EMPTY >> np.uint64(8)) & self.RANK_4
    
        if not self.isWhiteTurn:
            PAWN_MOVES = (self.BP << np.uint64(16)) & self.EMPTY & (self.EMPTY << np.uint64(8)) & self.RANK_5

        for i in range(64):
            move = {}
            if (PAWN_MOVES >> np.uint64(i)) & ONE == ONE:
                move['toString'] = makeField((i//8)+(color*2), (i % 8)) + "-"+makeField((i//8), i % 8)
                move['isHit'] = False
                moves.append(move)

        if self.enPassant != '-':
            RANK = self.FileMasks8[self.enPassant[0]]

            # en passant right
            PAWN_MOVES = (self.WP << ONE) & self.BP & self.RANK_5 & ~self.FILE_A & RANK
            
            if not self.isWhiteTurn:
                PAWN_MOVES = (self.BP >> ONE) & self.WP & self.RANK_4 & ~self.FILE_H & RANK
            
            for i in range(64):
                move = {}
                if (PAWN_MOVES >> np.uint64(i)) & ONE == ONE:
                    move['toString'] = makeField((i//8), i % 8-(color*1))+'x'+self.enPassant
                    move['isHit'] = True
                    move['enPassant'] = True
                    moves.append(move)

            # en passant left
            PAWN_MOVES = (self.WP >> ONE) & self.BP & self.RANK_5 & ~self.FILE_H & RANK

            if not self.isWhiteTurn:
                PAWN_MOVES = (self.BP << ONE) & self.WP & self.RANK_4 & ~self.FILE_A & RANK

            for i in range(64):
                move = {}
                if (PAWN_MOVES >> np.uint64(i)) & ONE == ONE:
                    move['toString'] = makeField((i//8), i % 8+(color*1))+'x'+self.enPassant
                    move['isHit'] = True
                    move['enPassant'] = True
                    moves.append(move)

        return moves

    def HAndVMoves(self, s):
        binaryS = ONE << np.uint64(s)
        possibilitiesHorizontal = (self.OCCUPIED - TWO * binaryS) ^ reverse(reverse(self.OCCUPIED) - TWO * reverse(binaryS))
        possibilitiesVertical = ((self.OCCUPIED & self.FileMasks82[s % 8]) - (TWO * binaryS)) ^ reverse(reverse(self.OCCUPIED & self.FileMasks82[s % 8]) - (TWO * reverse(binaryS)))
        return (possibilitiesHorizontal & self.RankMasks8[(s // 8)]) | (possibilitiesVertical & self.FileMasks82[s % 8])
    
    def DAndAntiDMoves(self, s:int):
        binaryS =ONE << np.uint64(s)
        possibilitiesDiagonal = ((self.OCCUPIED & self.DiagonalMasks8[(s // 8) + (s % 8)]) - (TWO * binaryS)) ^ reverse(reverse(self.OCCUPIED & self.DiagonalMasks8[(s // 8) + (s % 8)]) - (TWO * reverse(binaryS)))
        possibilitiesAntiDiagonal = ((self.OCCUPIED & self.AntiDiagonalMasks8[(s // 8) + 7 - (s % 8)]) - (TWO * binaryS)) ^ reverse(reverse(self.OCCUPIED & self.AntiDiagonalMasks8[(s // 8) + 7 - (s % 8)]) - (TWO * reverse(binaryS)))
        return (possibilitiesDiagonal & self.DiagonalMasks8[(s // 8) + (s % 8)]) | (possibilitiesAntiDiagonal & self.AntiDiagonalMasks8[(s // 8) + 7 - (s % 8)])
    
    def getMovesB(self, B):
        moves = []
        i = B&~(B - ONE)
        while(i != 0):
            iLocation = trailingZeros(i)
            possibility = self.DAndAntiDMoves(iLocation) & self.NOT_MY_PIECES
            j = possibility & ~(possibility - ONE)
            while (j != 0):
                move = {}
                index = trailingZeros(j)
                move['toString'] = "B"+makeField((iLocation//8),iLocation%8)+'-'+makeField((index//8),index%8)
                moves.append(move)
                possibility&=~j
                j = possibility & ~(possibility - ONE)
            B &= ~i
            i = B&~(B - ONE)
        return moves
    
    def getMovesR(self, R):
        moves = []
        i = R&~(R - ONE)
        while(i != 0):
            iLocation = trailingZeros(i)
            possibility = self.HAndVMoves(iLocation) & self.NOT_MY_PIECES
            j = possibility & ~(possibility - ONE)
            while (j != 0):
                move = {}
                index = trailingZeros(j)
                move['toString'] = "R"+makeField((iLocation//8),iLocation%8)+'-'+makeField((index//8),index%8)
                moves.append(move)
                possibility&=~j
                j = possibility & ~(possibility - ONE)
            R &= ~i
            i = R&~(R - ONE)
        return moves
    
    def getMovesQ(self, Q):
        moves = []
        i = Q&~(Q - ONE)
        while(i != 0):
            iLocation = trailingZeros(i)
            possibility = (self.DAndAntiDMoves(iLocation) | self.HAndVMoves(iLocation) )& self.NOT_MY_PIECES
            j = possibility & ~(possibility - ONE)
            while (j != 0):
                move = {}
                index = trailingZeros(j)
                move['toString'] = "Q"+makeField((iLocation//8),iLocation%8)+'-'+makeField((index//8),index%8)
                moves.append(move)
                possibility&=~j
                j = possibility & ~(possibility - ONE)
            Q &= ~i
            i = Q&~(Q - ONE)
        return moves
    
    def getMovesN(self, N):    
        moves = []
        i = N &~(N - ONE)
        # printBits(self.WHITE_PIECES, "notwhite")
        # printBits(self.FILE_AB)
        # printBits(self.FILE_GH)
        printBits(N)
        while i != 0:
            iLoc = trailingZeros(i) #loc of N
            if iLoc >  18:
                possibility = self.KNIGHT_SPAN << np.uint64(iLoc-18)
                printBits(possibility,">18") 
            else:
                possibility = self.KNIGHT_SPAN >> np.uint64(18 - iLoc)
                printBits(possibility,"<=18") 
            if iLoc%8 < 4:
                possibility &= ~self.FILE_GH & self.NOT_MY_PIECES
            else:
                possibility &= ~self.FILE_AB & self.NOT_MY_PIECES
            printBits(possibility,"nach if else")
            j = possibility &~(possibility-ONE)
            while j != 0:
                index = trailingZeros(j) 
                move = {}
                move['toString'] = "N"+makeField((iLoc//8),iLoc%8)+'-'+makeField((index//8),index%8)
                moves.append(move)
                possibility&=~j
                j=possibility&~(possibility- ONE)
            N &=~i
            i = N &~(N - ONE)
        return moves
        
  
# //////////////////
#
#       Tests
#
# ///////////////////
    
b = Board('rnbqkbnr/pppppppp/8/8/8/8/PPPPPPPP/RNBQKBNR b KQkq - 0 1')
print((b.getMoves()))
