from array import array
from random import *
import re
from time import time
import numpy as np
from helpers import *
from constants import *
from copy import copy
from algorithms import *


class Board:
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

    moves = []
    MOVE_HISTORY = []
    STATE_HISTORY = {} #später transpostion table?

    isWhiteTurn = True
    castleRight = "KQkq"
    castleRight2 = [True,True,True,True]
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
            self.castleRight2 = castleStrToArr(splittedFEN[2])
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
            binary = ZERO_STRING[i+1:] + "1" + ZERO_STRING[0:i]
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
            elif (self.WN >> np.uint64(i)) & ONE == ONE:
                newChessBoard[row][col] = "N"
            elif (self.WB >> np.uint64(i)) & ONE == ONE:
                newChessBoard[row][col] = "B"
            elif (self.WR >> np.uint64(i)) & ONE == ONE:
                newChessBoard[row][col] = "R"
            elif (self.WQ >> np.uint64(i)) & ONE == ONE:
                newChessBoard[row][col] = "Q"
            elif (self.WK >> np.uint64(i)) & ONE == ONE:
                newChessBoard[row][col] = "K"
            elif (self.BP >> np.uint64(i)) & ONE == ONE:
                newChessBoard[row][col] = "p"
            elif (self.BN >> np.uint64(i)) & ONE == ONE:
                newChessBoard[row][col] = "n"
            elif (self.BB >> np.uint64(i)) & ONE == ONE:
                newChessBoard[row][col] = "b"
            elif (self.BR >> np.uint64(i)) & ONE == ONE:
                newChessBoard[row][col] = "r"
            elif (self.BQ >> np.uint64(i)) & ONE == ONE:
                newChessBoard[row][col] = "q"
            elif (self.BK >> np.uint64(i)) & ONE == ONE:
                newChessBoard[row][col] = "k"

        return newChessBoard

    def getMoves(self):
        self.moves = []
        if self.isWhiteTurn:
            return self.possibleMovesW()
        else:
            return self.possibleMovesB()

    def possibleMovesW(self):
        #added BK to avoid illegal capture
        self.NOT_MY_PIECES = ~(self.WP|self.WN|self.WB|self.WR|self.WQ|self.WK|self.BK)
        #omitted WK to avoid illegal capture
        self.MY_PIECES = self.WP|self.WN|self.WB|self.WR|self.WQ
        self.OCCUPIED=self.WP|self.WN|self.WB|self.WR|self.WQ|self.WK|self.BP|self.BN|self.BB|self.BR|self.BQ|self.BK
        self.EMPTY=~self.OCCUPIED
        self.getMovesP()
        self.getMovesN(self.WN)
        self.getMovesB(self.WB)
        self.getMovesK(self.WK)
        self.getMovesQ(self.WQ)
        self.getMovesR(self.WR)
        return self.moves

        
    
    def possibleMovesB(self):
        #added WK to avoid illegal capture
        self.NOT_MY_PIECES=~(self.BP|self.BN|self.BB|self.BR|self.BQ|self.BK|self.WK)
        #omitted BK to avoid illegal capture
        self.MY_PIECES=self.BP|self.BN|self.BB|self.BR|self.BQ
        self.OCCUPIED=self.WP|self.WN|self.WB|self.WR|self.WQ|self.WK|self.BP|self.BN|self.BB|self.BR|self.BQ|self.BK
        self.EMPTY=~self.OCCUPIED
        self.getMovesP()
        self.getMovesB(self.BB)
        self.getMovesN(self.BN)
        self.getMovesQ(self.BQ)
        self.getMovesR(self.BR)
        self.getMovesK(self.BK)
        return self.moves

    
    def getMovesP(self):
        # exluding black king, because he can't be eaten
        self.BLACK_PIECES = self.BP | self.BN | self.BB | self.BR | self.BQ
        
        # same here
        self.WHITE_PIECES = self.WP | self.WN | self.WB | self.WR | self.WQ

        # beat right
        if self.isWhiteTurn:
            PAWN_MOVES = (self.WP >> np.uint64(7)) & self.BLACK_PIECES & ~FILE_A
            PAWN_MOVES_PROMO = (self.WP >> np.uint64(7)) & self.BLACK_PIECES & RANK_8 & ~FILE_A
            P = self.WP
            K = self.WK
            color = 1
            type = 'P' 
        else: 
            PAWN_MOVES = (self.BP << np.uint64(7)) & self.WHITE_PIECES  &~ FILE_H
            PAWN_MOVES_PROMO = (self.BP << np.uint64(7)) & self.WHITE_PIECES & RANK_1 & ~FILE_H
            P = self.BP
            K = self.BK
            color = -1
            type = 'p'

        for i in range(64):
            isPromo = False 
            move = {}
            if (PAWN_MOVES_PROMO >> np.uint64(i)) & ONE == ONE:
                move['isPromo'] = True
                isPromo = True
            if (PAWN_MOVES >> np.uint64(i)) & ONE  == ONE :
                move['toString'] = makeField((i//8)+(color*1), (i % 8)-(color*1)) + "x" + makeField((i//8), i % 8)
                move['from'] = np.uint64(((i//8)+(color*1))*8+((i % 8)-(color*1)))
                move['to'] = np.uint64((i//8)*8 + (i % 8))
                move['type'] = type
                #check if K is in danger
                previewBoardP = self.doMoveHelper(move, P)
                boardAll = self.getModifiedBoard(type, previewBoardP)
                unsafe = self.unsafeFor(self.isWhiteTurn, boardAll, move['to'])
                if unsafe & K == 0:
                    if isPromo:
                        self.promoHelper(self.isWhiteTurn, move)
                    else:
                        self.moves.append(move)

        # beat left
        if self.isWhiteTurn:
            PAWN_MOVES = (self.WP >> np.uint64(9)) & self.BLACK_PIECES  & ~ FILE_H
            PAWN_MOVES_PROMO = (self.WP >> np.uint64(9)) & self.BLACK_PIECES & RANK_8 & ~FILE_H
            P = self.WP
            K = self.WK
        else:
            PAWN_MOVES = (self.BP << np.uint64(9)) & self.WHITE_PIECES  & ~ FILE_A
            PAWN_MOVES_PROMO = (self.BP << np.uint64(9)) & self.WHITE_PIECES & RANK_1 & ~FILE_A
            P = self.BP
            K = self.BK

        for i in range(64):
            move = {}
            isPromo = False
            if (PAWN_MOVES_PROMO >> np.uint64(i)) & ONE == ONE:
                move['isPromo'] = True
                isPromo = True
            if (PAWN_MOVES >> np.uint64(i)) & ONE == ONE:
                move['toString'] = makeField((i//8)+(color*1), (i % 8)+(color*1)) + "x"+makeField((i//8), i % 8)
                move['from'] = np.uint64(((i//8)+(color*1))*8+((i % 8)-(color*1))) 
                move['to'] = np.uint64((i//8)*8+(i % 8))
                move['type'] = type
                #check if K is in danger
                previewBoardP = self.doMoveHelper(move, P)
                boardAll = self.getModifiedBoard(type, previewBoardP)
                unsafe = self.unsafeFor(self.isWhiteTurn, boardAll, move['to'])
                if unsafe & K == 0:
                    if isPromo:
                        self.promoHelper(self.isWhiteTurn, move)
                    else:
                        self.moves.append(move)

        # move 1 forward
        if self.isWhiteTurn:
            PAWN_MOVES = (self.WP >> np.uint64(8)) & self.EMPTY 
            PAWN_MOVES_PROMO = (self.WP >> np.uint64(8)) & self.EMPTY & RANK_8
            P = self.WP
            K = self.WK
        else:
            PAWN_MOVES = (self.BP << np.uint64(8)) & self.EMPTY
            PAWN_MOVES_PROMO = (self.BP << np.uint64(8)) & self.EMPTY & RANK_1
            P = self.BP
            K = self.BK

        for i in range(64):
            move = {}
            isPromo = False
            if (PAWN_MOVES_PROMO >> np.uint64(i)) & ONE == ONE:
                move['isPromo'] = True
                isPromo = True
            if (PAWN_MOVES >> np.uint64(i)) & ONE == ONE:
                move['toString'] = makeField((i//8)+(color*1), (i % 8)) + "-"+makeField((i//8), i % 8)
                move['from'] = np.uint64(((i//8)+(color*1))*8+(i % 8))
                move['to'] = np.uint64((i//8)*8+(i%8))
                move['type'] = type
                #check if K is in danger
                previewBoardP = self.doMoveHelper(move, P)
                boardAll = self.getModifiedBoard(type, previewBoardP)
                unsafe = self.unsafeFor(self.isWhiteTurn, boardAll, move['to'])
                if unsafe & K == 0:
                    if isPromo:
                        self.promoHelper(self.isWhiteTurn, move)
                    else:
                        self.moves.append(move)

        # move 2 forward
        if self.isWhiteTurn:
            PAWN_MOVES = (self.WP >> np.uint64(16)) & self.EMPTY & (self.EMPTY >> np.uint64(8)) & RANK_4
            P = self.WP
            K = self.WK
        else:
            PAWN_MOVES = (self.BP << np.uint64(16)) & self.EMPTY & (self.EMPTY << np.uint64(8)) & RANK_5
            P = self.BP
            K = self.BK

        for i in range(64):
            move = {}
            if (PAWN_MOVES >> np.uint64(i)) & ONE == ONE:
                move['toString'] = makeField((i//8)+(color*2), (i % 8)) + "-"+makeField((i//8), i % 8)
                move['from'] = np.uint64(((i//8)+(color*2))*8+(i%8))
                move['to'] = np.uint64((i//8)*8+(i % 8))
                move['type'] = type
                move['double'] = makeField((i//8)+(color*1), i % 8)
                #check if K is in danger
                previewBoardP = self.doMoveHelper(move, P)
                boardAll = self.getModifiedBoard(type, previewBoardP)
                unsafe = self.unsafeFor(self.isWhiteTurn, boardAll, move['to'])
                if unsafe & K == 0:
                    self.moves.append(move)

        if self.enPassant != '-':
            RANK = FileMasks8[self.enPassant[0]]

            # en passant right
            if self.isWhiteTurn:
                PAWN_MOVES = (self.WP << ONE) & self.BP & RANK_5 & ~FILE_A & RANK
                P = self.WP
                K = self.WK
            else:
                PAWN_MOVES = (self.BP >> ONE) & self.WP & RANK_4 & ~FILE_H & RANK
                P = self.BP
                K = self.BK
            
            for i in range(64):
                move = {}
                if (PAWN_MOVES >> np.uint64(i)) & ONE == ONE:
                    move['toString'] = makeField((i//8), i % 8-(color*1))+'x'+makeField((i//8)-(color*1), i % 8)
                    move['from'] = np.uint64(((i//8)*8)+(i%8-(color*1)))
                    move['to'] = np.uint64(((i//8)-(color*1))*8+(i % 8))
                    move['type'] = type
                    move['enPassant'] = True
                    #check if K is in danger
                    previewBoardP = self.doMoveHelper(move, P)
                    boardAll = self.getModifiedBoard(type, previewBoardP)
                    if self.isWhiteTurn:
                        destination = np.uint64(((((i//8)-(color*1))+1)*8)+(i % 8))
                    else:
                        destination = np.uint64(((((i//8)-(color*1))-1)*8)+(i % 8))
                    unsafe = self.unsafeFor(self.isWhiteTurn, boardAll, destination)
                    if unsafe & K == 0:
                        move['enemy'] = destination
                        self.moves.append(move)

            # en passant left
            if self.isWhiteTurn:
                PAWN_MOVES = (self.WP >> ONE) & self.BP & RANK_5 & ~FILE_H & RANK
                P = self.WP
                K = self.WK
            else:
                PAWN_MOVES = (self.BP << ONE) & self.WP & RANK_4 & ~FILE_A & RANK
                P = self.BP
                K = self.BK

            for i in range(64):
                move = {}
                if (PAWN_MOVES >> np.uint64(i)) & ONE == ONE:
                    move['toString'] = makeField((i//8), i % 8+(color*1))+'x'+ makeField((i//8) -(color*1), i % 8)
                    move['from'] = np.uint64(((i//8)*8)+(i % 8+(color*1)))
                    move['to'] = np.uint64(((i//8)-(color*1))*8+(i % 8))
                    move['type'] = type
                    move['enPassant'] = True
                    #check if K is in danger
                    previewBoardP = self.doMoveHelper(move, P)
                    boardAll = self.getModifiedBoard(type, previewBoardP)
                    if self.isWhiteTurn:
                        destination = np.uint64(((((i//8)-(color*1))+1)*8)+(i % 8))
                    else:
                        destination = np.uint64(((((i//8)-(color*1))-1)*8)+(i % 8))
                    unsafe = self.unsafeFor(self.isWhiteTurn, boardAll, destination)
                    if unsafe & K == 0:
                        move['enemy'] = destination
                        self.moves.append(move)
    
    def promoHelper(self, isWhiteTurn:bool ,move):
        moveR = copy(move)
        moveR['promoType'] = 'R' if isWhiteTurn else 'r'
        self.moves.append(moveR)
        moveQ = copy(move)
        moveQ['promoType'] = 'Q' if isWhiteTurn else 'q'
        self.moves.append(moveQ)
        moveB = copy(move)
        moveB['promoType'] = 'B' if isWhiteTurn else 'b'
        self.moves.append(moveB)
        moveN = copy(move)
        moveN['promoType'] = 'N' if isWhiteTurn else 'n'
        self.moves.append(moveN)

    def HAndVMoves(self, s, OCCUPIED_CUSTOM = None):
        OCCUPIED = OCCUPIED_CUSTOM if OCCUPIED_CUSTOM else self.WP|self.WN|self.WB|self.WR|self.WQ|self.WK|self.BP|self.BN|self.BB|self.BR|self.BQ|self.BK
        binaryS = ONE << np.uint64(s)
        possibilitiesHorizontal = (OCCUPIED - TWO * binaryS) ^ reverse(reverse(OCCUPIED) - TWO * reverse(binaryS))
        possibilitiesVertical = ((OCCUPIED & FileMasks82[s % 8]) - (TWO * binaryS)) ^ reverse(reverse(OCCUPIED & FileMasks82[s % 8]) - (TWO * reverse(binaryS)))
        return (possibilitiesHorizontal & RankMasks8[(s // 8)]) | (possibilitiesVertical & FileMasks82[s % 8])
    
    def DAndAntiDMoves(self, s:int, OCCUPIED_CUSTOM = None):
        OCCUPIED = OCCUPIED_CUSTOM if OCCUPIED_CUSTOM else self.WP|self.WN|self.WB|self.WR|self.WQ|self.WK|self.BP|self.BN|self.BB|self.BR|self.BQ|self.BK
        binaryS =ONE << np.uint64(s)
        possibilitiesDiagonal = ((OCCUPIED & DiagonalMasks8[(s // 8) + (s % 8)]) - (TWO * binaryS)) ^ reverse(reverse(OCCUPIED & DiagonalMasks8[(s // 8) + (s % 8)]) - (TWO * reverse(binaryS)))
        possibilitiesAntiDiagonal = ((OCCUPIED & AntiDiagonalMasks8[(s // 8) + 7 - (s % 8)]) - (TWO * binaryS)) ^ reverse(reverse(OCCUPIED & AntiDiagonalMasks8[(s // 8) + 7 - (s % 8)]) - (TWO * reverse(binaryS)))
        return (possibilitiesDiagonal & DiagonalMasks8[(s // 8) + (s % 8)]) | (possibilitiesAntiDiagonal & AntiDiagonalMasks8[(s // 8) + 7 - (s % 8)])
    
    def getMovesB(self, B):
        if self.isWhiteTurn:
            K = self.WK
            type = 'B'
        else:
            K = self.BK
            type = 'b'
        i = B&~(B - ONE)
        while(i != 0):
            iLocation = trailingZeros(i)
            possibility = self.DAndAntiDMoves(iLocation) & self.NOT_MY_PIECES
            j = possibility & ~(possibility - ONE)
            while (j != 0):
                move = {}
                index = trailingZeros(j)
                move['toString'] = "B"+makeField((iLocation//8),iLocation%8)+'-'+makeField((index//8),index%8)
                move['from'] = np.uint64(((iLocation//8)*8)+(iLocation%8))
                move['to'] = np.uint64(((index//8)*8)+(index%8))
                move['type'] = type
                #check if K is in danger
                previewBoard = self.doMoveHelper(move, B)
                boardAll = self.getModifiedBoard(type, previewBoard)
                unsafe = self.unsafeFor(self.isWhiteTurn, boardAll, move['to'])
                if unsafe & K == 0:
                    self.moves.append(move)

                possibility&=~j
                j = possibility & ~(possibility - ONE)
            B &= ~i
            i = B&~(B - ONE)
    
    def getMovesR(self, R):
        if self.isWhiteTurn:
            K = self.WK
            type = 'R'
        else:
            K = self.BK
            type = 'r'
        i = R&~(R - ONE)
        while(i != 0):
            iLocation = trailingZeros(i)
            possibility = self.HAndVMoves(iLocation) & self.NOT_MY_PIECES
            j = possibility & ~(possibility - ONE)
            while (j != 0):
                move = {}
                index = trailingZeros(j)
                move['toString'] = "R"+makeField((iLocation//8),iLocation%8)+'-'+makeField((index//8),index%8)
                move['from'] = np.uint64(((iLocation//8)*8)+(iLocation%8))
                move['to'] = np.uint64(((index//8)*8)+(index%8))
                move['type'] = type
                #check if K is in danger
                previewBoard = self.doMoveHelper(move, R)
                boardAll = self.getModifiedBoard(type, previewBoard)
                unsafe = self.unsafeFor(self.isWhiteTurn, boardAll, move['to'])
                if unsafe & K == 0:
                    self.moves.append(move)      

                possibility&=~j
                j = possibility & ~(possibility - ONE)
            R &= ~i
            i = R&~(R - ONE)
    
    def getMovesQ(self, Q):
        if self.isWhiteTurn:
            K = self.WK
            type = 'Q'
        else:
            K = self.BK
            type = 'q'
        i = Q&~(Q - ONE)
        while(i != 0):
            iLocation = trailingZeros(i)
            possibility = (self.DAndAntiDMoves(iLocation) | self.HAndVMoves(iLocation) )& self.NOT_MY_PIECES
            j = possibility & ~(possibility - ONE)
            while (j != 0):
                move = {}
                index = trailingZeros(j)
                move['toString'] = "Q"+makeField((iLocation//8),iLocation%8)+'-'+makeField((index//8),index%8)
                move['from'] = np.uint64(((iLocation//8)*8)+(iLocation%8))
                move['to'] = np.uint64(((index//8)*8)+(index%8))
                move['type'] = type
                #check if K is in danger
                previewBoard = self.doMoveHelper(move, Q)
                boardAll = self.getModifiedBoard(type, previewBoard)
                unsafe = self.unsafeFor(self.isWhiteTurn, boardAll, move['to'])
                if unsafe & K == 0:
                    self.moves.append(move)

                possibility&=~j
                j = possibility & ~(possibility - ONE)
            Q &= ~i
            i = Q&~(Q - ONE)
    
    def getMovesN(self, N):  
        if self.isWhiteTurn:
            K = self.WK
            type = 'N'
        else:
            K = self.BK
            type = 'n'  
        i = N &~(N - ONE)
        while i != 0:
            iLoc = trailingZeros(i)
            if iLoc >  18:
                possibility = KNIGHT_SPAN << np.uint64(iLoc-18)
            else:
                possibility = KNIGHT_SPAN >> np.uint64(18 - iLoc)
            if iLoc%8 < 4:
                possibility &= ~FILE_GH & self.NOT_MY_PIECES
            else:
                possibility &= ~FILE_AB & self.NOT_MY_PIECES
            j = possibility &~(possibility-ONE)
            while j != 0:
                index = trailingZeros(j) 
                move = {}
                move['toString'] = "N"+makeField((iLoc//8),iLoc%8)+'-'+makeField((index//8),index%8)
                move['from'] = np.uint64(((iLoc//8)*8)+(iLoc%8))
                move['to'] = np.uint64(((index//8)*8)+(index%8))
                move['type'] = type
                #check if K is in danger
                previewBoard = self.doMoveHelper(move, N)
                boardAll = self.getModifiedBoard(type, previewBoard)
                unsafe = self.unsafeFor(self.isWhiteTurn, boardAll, move['to'])
                if unsafe & K == 0:
                    self.moves.append(move)      

                possibility&=~j
                j=possibility&~(possibility- ONE)
            N &=~i
            i = N &~(N - ONE)
    
    def getMovesK(self, K):
        if self.isWhiteTurn:
            type = 'K'
            castleRightK = 'K' in self.castleRight #castleRight2 ist vielleicht besser als string basiert
            castleRightQ = 'Q' in self.castleRight
            castleK = CASTLE_K
            castleQ = CASTLE_Q
        else:
            type = 'k'
            castleRightK = 'k' in self.castleRight
            castleRightQ = 'q' in self.castleRight
            castleK = CASTLE_k
            castleQ = CASTLE_q

        isWhiteKing = K & self.WK > 0 
        iLoc = trailingZeros(K)
        if iLoc >  9:
            possibility = KING_SPAN << np.uint64(iLoc-9)
        else:
            possibility = KING_SPAN >> np.uint64(9 - iLoc)
        if iLoc%8 < 4:
            possibility &= ~FILE_GH & self.NOT_MY_PIECES
        else:
            possibility &= ~FILE_AB & self.NOT_MY_PIECES
        j = possibility &~(possibility-ONE)
        safe = ~self.unsafeFor(isWhiteKing)

        if castleRightK and castleK & safe & self.EMPTY == castleK :
            move = {}
            move['toString'] = "0-0"
            move['type'] = type
            move['castle'] = "k"
            self.moves.append(move)
        if castleRightQ and castleQ & safe & self.EMPTY == castleQ :
            move = {}
            move['toString'] = "0-0-0"
            move['type'] = type
            move['castle'] = "q"
            self.moves.append(move)
            
        while j != 0:
            if j & safe != 0: #filters out unsafe fields
                index = trailingZeros(j) 
                move = {}
                move['toString'] = "K"+makeField((iLoc//8),iLoc%8)+'-'+makeField((index//8),index%8)
                move['from'] = np.uint64(((iLoc//8)*8)+(iLoc%8))
                move['to'] = np.uint64(((index//8)*8)+(index%8))
                move['type'] = type
                self.moves.append(move)
            possibility&=~j
            j=possibility&~(possibility- ONE)

    def unsafeFor(self, isForWhite: bool, board:np.uint64 = None, destination: np.uint64 = None):
        """
        Generates a bitboard with all fields that would put the King of the color set through `isFormWhite` in check/danger.

        Args:
            `isForWhite` (bool): if `True` bitboard shows fields that are not safe for white pieces, if `False` then same for black 

        Returns:
            bitboard with unsafe fields for given color
        """
        if isForWhite:
            P = self.BP
            N = self.BN
            QB = self.BQ|self.BB
            QR = self.BQ|self.BR
            K = self.BK
            #black pawn
            unsafe = (P<<np.uint64(7)) & ~FILE_H 
            unsafe |= (P<<np.uint64(9)) & ~FILE_A
        else:
            P = self.WP
            N = self.WN
            QB = self.WQ|self.WB
            QR = self.WQ|self.WR
            K = self.WK
            #white pawn
            unsafe = (P>>np.uint64(7)) & ~FILE_A 
            unsafe |= (P>>np.uint64(9)) & ~FILE_H

        if destination:
            P&=~(ONE<<destination)
            N&=~(ONE<<destination)
            QB&=~(ONE<<destination)
            QR&=~(ONE<<destination)
            K&=~(ONE<<destination)
        
        if board:
            OCCUPIED = board|P|N|QB|QR|K
        else:
            OCCUPIED = None
        
        #knight
        i = N &~(N - ONE)
        while i != 0:
            iLoc = trailingZeros(i)
            if iLoc > 18:
                possibility = KNIGHT_SPAN << np.uint64(iLoc - 18)
            else:
                possibility = KNIGHT_SPAN >> np.uint64(18 - iLoc)
            if iLoc % 8 < 4:
                possibility &= ~FILE_GH
            else:
                possibility &= ~FILE_AB
            unsafe |= possibility
            N &=~i
            i = N & ~(N-ONE)
            
        #(anti)diagonal sliding pieces (bishop & queen)
        i = QB &~(QB-ONE)
        while i != 0:
            iLoc = trailingZeros(i)
            possibility = self.DAndAntiDMoves(iLoc, OCCUPIED)
            unsafe |= possibility
            QB&=~i
            i=QB&~(QB-ONE)
            
        #staight sliding pieces (rook & queen)
        i = QR &~(QR-ONE)
        while i != 0:
            iLoc = trailingZeros(i)
            possibility = self.HAndVMoves(iLoc, OCCUPIED)
            unsafe |= possibility
            QR&=~i
            i=QR&~(QR-ONE)
        
        #king
        iLoc = trailingZeros(K)
        if iLoc > 9:
            possibility = KING_SPAN<<np.uint64(iLoc-9)
        else:
            possibility = KING_SPAN>>np.uint64(9 -iLoc)
        if iLoc % 8 < 4:
            possibility &=~FILE_GH
        else:
            possibility &=~FILE_AB
        unsafe |= possibility
        
        return unsafe

    def getModifiedBoard(self, type:str, piece: np.uint64):
        if type == 'P':
            return self.WB | self.WK | self.WN | self.WQ | self.WR | piece
        if type == 'B':
            return self.WP | self.WK | self.WN | self.WQ | self.WR | piece
        if type == 'N':
            return self.WP | self.WB | self.WQ | self.WK | self.WR | piece
        if type == 'R':
            return self.WP | self.WB | self.WQ | self.WK | self.WN | piece 
        if type == 'Q':
            return self.WP | self.WB | self.WR | self.WK | self.WN | piece
        if type == 'p':
            return self.BB | self.BK | self.BN | self.BQ | self.BR | piece
        if type == 'b':
            return self.BP | self.BK | self.BN | self.BQ | self.BR | piece
        if type == 'n':
            return self.BP | self.BB | self.BQ | self.BK | self.BR | piece
        if type == 'r':
            return self.BP | self.BB | self.BQ | self.BK | self.BN | piece
        if type == 'q':
            return self.BP | self.BB | self.BR | self.BK | self.BN | piece 

    def doMove(self, move):
        undoMove = []
        type = move['type']
        if type.isupper():
            if type == 'P':
                self.WP = self.doMoveHelperPawn(move, self.WP, undoMove)
            elif type == 'B':
                self.WB = self.doMoveHelper(move, self.WB, undoMove)
            elif type == 'N':
                self.WN = self.doMoveHelper(move, self.WN, undoMove)
            elif type == 'R':
                self.WR = self.doMoveHelper(move, self.WR, undoMove)
                if self.WR & FILE_A & RANK_1 == 0:
                    self.castleRight = self.castleRight.replace('K','')
                elif self.WR & FILE_H & RANK_1 == 0:
                    self.castleRight = self.castleRight.replace('Q','')
            elif type == 'K':
                self.WK = self.doMoveHelper(move, self.WK, undoMove)
                undoMove.append(('castle', self.castleRight))
                self.castleRight = self.castleRight.replace('KQ','')
            elif type == 'Q':
                self.WQ = self.doMoveHelper(move, self.WQ, undoMove)

            if move['type'] =='P' and move.get('enPassant'):
                destination = move['enemy']
                self.clearDestination(True, destination, undoMove)   
            elif not move.get('castle'):
                destination = move['to']
                self.clearDestination(True, destination, undoMove)   
        else:
            if type == 'p':
                self.BP = self.doMoveHelperPawn(move, self.BP, undoMove)
            elif type == 'b':
                self.BB = self.doMoveHelper(move, self.BB, undoMove)
            elif type == 'n':
                self.BN = self.doMoveHelper(move, self.BN, undoMove)
            elif type == 'r':
                self.BR = self.doMoveHelper(move, self.BR, undoMove)
                if self.BR & FILE_A & RANK_8 == 0:
                    self.castleRight = self.castleRight.replace('k','')
                elif self.WR & FILE_H & RANK_8 == 0:
                    self.castleRight = self.castleRight.replace('q','')
            elif type == 'k':
                self.BK = self.doMoveHelperKing(move, self.BK, undoMove)
                undoMove.append(('castle', self.castleRight))
                self.castleRight = self.castleRight.replace('kq','')
            elif type == 'q':
                self.BQ = self.doMoveHelper(move, self.BQ, undoMove)

            if move['type'] == 'p' and move.get('enPassant'):
                destination = move['enemy']
                self.clearDestination(False, destination, undoMove) 
            elif not move.get('castle') :   
                destination = move['to']
                self.clearDestination(False, destination, undoMove) 

        self.MOVE_HISTORY.append(undoMove)
        boardString = getBoardStr(self) #might be replaced with hash function later
        if boardString in self.STATE_HISTORY:
            self.STATE_HISTORY[boardString] += 1
        else:
            self.STATE_HISTORY[boardString] = 1

        self.isWhiteTurn = not self.isWhiteTurn
        if move.get('double'):
            self.enPassant = move['double']
        else:
            self.enPassant = '-'

    def doMoveHelper(self, move, BOARD:np.uint64, undoMove:array = None):
        if undoMove is not None:
            undoMove.append((move['type'], BOARD))

        start = move['from']
        end = move['to']
        if (((BOARD >> start) & ONE) == ONE):
            BOARD &= ~(ONE << start)
            BOARD |= (ONE << end)
        return BOARD

    def doMoveHelperKing(self, move, BOARD, undoMove:array = None):
        if not move.get('castle'):
            start = move['from']
            end = move['to']
            if (((BOARD >> start) & ONE) == ONE):
                undoMove.append((move['type'], BOARD))
                BOARD &= ~(ONE << start)
                BOARD |= (ONE << end)
        else:
            type = move['type']
            castle = move ['castle']
            if type.isupper():
                if castle == 'q':
                    undoMove.append(type, BOARD)
                    undoMove.append(('r', self.WR))
                    BOARD =(BOARD >> ONE)
                    self.WR ^=(np.uint64(72057594037927936))
                    self.WR |=(ONE << np.uint64(60))
                elif castle =='k':
                    undoMove.append(type, BOARD)
                    undoMove.append(('r', self.WR))
                    BOARD =(BOARD << ONE)
                    self.WR ^=(np.uint64(9223372036854775808))
                    self.WR |=(ONE << np.uint64(60))

            else:
                if castle == 'q':
                    undoMove.append((type, BOARD))
                    undoMove.append(('r', self.BR))
                    BOARD = BOARD >> ONE 
                    self.BR ^= np.uint64(1)
                    self.BR |=(ONE << np.uint64(4))
                elif castle == 'k':
                    undoMove.append((type, BOARD))
                    undoMove.append(('r', self.BR))
                    BOARD = BOARD << ONE 
                    self.BR ^= np.uint64(128)
                    self.BR |=(ONE << np.uint64(4))
        return BOARD


    def doMoveHelperPawn(self, move, BOARD, undoMove:array = None):
        oldBoard = BOARD
        start = move['from']
        end = move['to']
        if not move.get('isPromo'):
            if (((BOARD >> start) & ONE) == ONE):
                BOARD &= ~(ONE << start)
                BOARD |= (ONE << end)
                undoMove.append((move['type'], oldBoard))
        else:
            if (((BOARD >> start) & ONE) == ONE):
                BOARD &= ~(ONE << start)
                type = move['promoType']
                if type == 'Q':
                    oldBoard2 = self.WQ
                    self.WQ |= (ONE << end)
                elif type == 'R':
                    oldBoard2 = self.WR
                    self.WR |= (ONE << end)
                elif type == 'B':
                    oldBoard2 = self.WB
                    self.WB |= (ONE << end)
                elif type == 'N':
                    oldBoard2 = self.WN
                    self.WN |= (ONE << end)
                elif type == 'q':
                    oldBoard2 = self.BQ
                    self.BQ |= (ONE << end)
                elif type == 'r':
                    oldBoard2 = self.BR
                    self.BR |= (ONE << end)
                elif type == 'b':
                    oldBoard2 = self.BB
                    self.BB |= (ONE << end)
                elif type == 'n':
                    oldBoard2 = self.BN
                    self.BN |= (ONE << end)

                undoMove.extend([(move['type'], oldBoard),(type,oldBoard2)])

        return BOARD

    def clearDestination(self, isWhite:bool, destination:np.uint64, undoMove:array):
        if isWhite:
            if (((self.BP >> destination) & ONE) == ONE):
                undoMove.append(('p', self.BP))
                self.BP &= ~(ONE << destination)
            elif (((self.BN >> destination) & ONE) == ONE):
                undoMove.append(('n', self.BN))
                self.BN&=~(ONE<<destination)
            elif (((self.BQ >> destination) & ONE) == ONE):
                undoMove.append(('q', self.BQ))
                self.BQ&=~(ONE<<destination)
            elif (((self.BB >> destination) & ONE) == ONE):
                undoMove.append(('b', self.BB))
                self.BB&=~(ONE<<destination)
            elif (((self.BR >> destination) & ONE) == ONE):
                undoMove.append(('r', self.BR))
                self.BR&=~(ONE<<destination)
            elif (((self.BK >> destination) & ONE) == ONE):
                undoMove.append(('k', self.BK))
                self.BK&=~(ONE<<destination) 
        else:
            if (((self.WP >> destination) & ONE) == ONE):
                undoMove.append(('P', self.WP))
                self.WP &= ~(ONE << destination)
            elif (((self.WN >> destination) & ONE) == ONE):
                undoMove.append(('N', self.WN))
                self.WN&=~(ONE<<destination)
            elif (((self.WQ >> destination) & ONE) == ONE):
                undoMove.append(('Q', self.WQ))
                self.WQ&=~(ONE<<destination)
            elif (((self.WB >> destination) & ONE) == ONE):
                undoMove.append(('B', self.WB))
                self.WB&=~(ONE<<destination)
            elif (((self.WR >> destination) & ONE) == ONE):
                undoMove.append(('R', self.WR))
                self.WR&=~(ONE<<destination)
            elif (((self.WK >> destination) & ONE) == ONE):
                undoMove.append(('K', self.WK))
                self.WK&=~(ONE<<destination) 

    def undoLastMove(self):
        last, self.MOVE_HISTORY = self.MOVE_HISTORY[-1], self.MOVE_HISTORY[:-1]
        self.STATE_HISTORY[getBoardStr(self)]-=1 #might be replaced with hash function later
        
        for type, value in last:
            if type =='P':
                self.WP = value
            elif type == 'B':
                self.WB = value
            elif type == 'N':
                self.WN = value
            elif type == 'R':
                self.WR = value
            elif type == 'Q':
                self.WQ = value
            elif type == 'K':
                self.WK = value
            elif type =='p':
                self.BP = value
            elif type == 'b':
                self.BB = value
            elif type == 'n':
                self.BN = value
            elif type == 'r':
                self.BR = value
            elif type == 'q':
                self.BQ = value
            elif type == 'k':
                self.BK = value
            elif type == 'castle':
                self.castleRight = value
        self.isWhiteTurn = not self.isWhiteTurn
        self.enPassant = '-' #ist aber nicht immer der Fall. ?
        
    
    def printBoard(self):
        printBits(self.WP, 'White Pawns')
        printBits(self.WN, 'White Knights')
        printBits(self.WB, 'White Bishops')
        printBits(self.WQ, 'White Queen')
        printBits(self.WR, 'White Rooks')
        printBits(self.WK, 'White King')
        print('===========================')
        printBits(self.BP, 'Black Pawns')
        printBits(self.BN, 'Black Knights')
        printBits(self.BB, 'Black Bishops')
        printBits(self.BQ, 'Black Queen')
        printBits(self.BR, 'Black Rooks')
        printBits(self.BK, 'Black King')
        
    def evaluate(self):
        value = 0
        colorfactor = -1
        if self.isWhiteTurn:
            colorfactor = 1

        pawns = 1*(countSetBits(self.WP) - countSetBits(self.BP))
        knightsAndBishops = 3*(countSetBits(self.WN | self.WB) - countSetBits(self.BN | self.BB))
        rooks = 5* (countSetBits(self.WR) - countSetBits(self.BR))
        queens = 9 * (countSetBits(self.WQ) - countSetBits(self.BQ))
        squarePieceBalance = colorfactor*(queens + rooks + knightsAndBishops + pawns)
        
        simpleMobility = colorfactor*(len(self.possibleMovesW()) - len(self.possibleMovesB()))
        
        value = squarePieceBalance + simpleMobility
        
        if self.isCheck(): value = -10
        if self.isRemis(): value = -100
        if self.isCheckMate(): value = -10000
        if self.isKingOfTheHill(): value = 10000
        
        return value 
        
    
# //////////////////////////////////////////////////////
#
#                    State checks
#
# //////////////////////////////////////////////////////

    def isGameDone(self):
        return self.isCheckMate() or self.isKingOfTheHill() or self.isRemis()
        
    def isCheck(self):
        K = self.BK
        if (self.isWhiteTurn):
            K = self.WK
        return self.unsafeFor(self.isWhiteTurn) & K > 0
    
    def isCheckMate(self):
        return len(self.getMoves()) == 0 and self.isCheck()
    
    def isKingOfTheHill(self):
        K = self.BK
        if (self.isWhiteTurn):
            K = self.WK
        return HILLS & K > 0
    
    def isRemis(self):
        return self.is3Fold() or self.is50Rule() or self.isStaleMate()
        
    def isStaleMate(self):
        return len(self.getMoves()) == 0 and not self.isCheck()
        
    def is50Rule(self):
        return self.halfmoveClock == 50 # or 100??

    def is3Fold(self):
        for key in self.STATE_HISTORY:
            if self.STATE_HISTORY[key] >= 3:
                return True
        return False

