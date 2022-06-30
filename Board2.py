import re
import numpy as np
from helpers import *
from constants import *
from copy import copy


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
        return self.getMovesP()+self.getMovesB(self.WB)+self.getMovesN(self.WN)+self.getMovesQ(self.WQ)+self.getMovesR(self.WR)+self.getMovesK(self.WK)

        
    
    def possibleMovesB(self) :
        #added WK to avoid illegal capture
        self.NOT_MY_PIECES=~(self.BP|self.BN|self.BB|self.BR|self.BQ|self.BK|self.WK)
        #omitted BK to avoid illegal capture
        self.MY_PIECES=self.BP|self.BN|self.BB|self.BR|self.BQ
        self.OCCUPIED=self.WP|self.WN|self.WB|self.WR|self.WQ|self.WK|self.BP|self.BN|self.BB|self.BR|self.BQ|self.BK
        self.EMPTY=~self.OCCUPIED
        return self.getMovesP()+self.getMovesB(self.BB)+self.getMovesN(self.BN)+self.getMovesQ(self.BQ)+self.getMovesR(self.BR)+self.getMovesK(self.BK)

    
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
        PAWN_MOVES = (self.WP >> np.uint64(7)) & self.BLACK_PIECES & ~FILE_A
        PAWN_MOVES_PROMO = (self.WP >> np.uint64(7)) & self.BLACK_PIECES & RANK_8 & ~FILE_A

        if not self.isWhiteTurn:
            PAWN_MOVES = (self.BP << np.uint64(7)) & self.WHITE_PIECES  &~ FILE_H
            PAWN_MOVES_PROMO = (self.BP << np.uint64(7)) & self.WHITE_PIECES & RANK_1 & ~FILE_H
        
        for i in range(64):
            isPromo = False 
            move = {}
            if (PAWN_MOVES_PROMO >> np.uint64(i)) & ONE == ONE:
                move['isPromo'] = True
                move['isWhite'] = self.isWhiteTurn
                isPromo = True
            if (PAWN_MOVES >> np.uint64(i)) & ONE  == ONE :
                move['toString'] = makeField((i//8)+(color*1), (i % 8)-(color*1)) + "x" + makeField((i//8), i % 8)
                move['from'] = ((i//8)+(color*1),(i % 8)-(color*1))
                move['to'] = ((i//8), i % 8)
                move['isPawn'] = True
                if isPromo:
                    self.promoHelper(move, moves)
                else:
                    moves.append(move)

        # beat left
        PAWN_MOVES = (self.WP >> np.uint64(9)) & self.BLACK_PIECES  & ~ FILE_H
        PAWN_MOVES_PROMO = (self.WP >> np.uint64(9)) & self.BLACK_PIECES & RANK_8 & ~FILE_H

        if not self.isWhiteTurn:
            PAWN_MOVES = (self.BP << np.uint64(9)) & self.WHITE_PIECES  & ~ FILE_A
            PAWN_MOVES_PROMO = (self.BP << np.uint64(9)) & self.WHITE_PIECES & RANK_1 & ~FILE_A

        for i in range(64):
            move = {}
            isPromo = False
            if (PAWN_MOVES_PROMO >> np.uint64(i)) & ONE == ONE:
                move['isPromo'] = True
                move['isWhite'] = self.isWhiteTurn
                isPromo = True
            if (PAWN_MOVES >> np.uint64(i)) & ONE == ONE:
                move['toString'] = makeField((i//8)+(color*1), (i % 8)+(color*1)) + "x"+makeField((i//8), i % 8)
                move['from'] =((i//8)+(color*1), (i % 8)-(color*1)) 
                move['to'] = ((i//8), i % 8)
                move['isPawn'] = True
                if isPromo:
                    self.promoHelper(move, moves)
                else:
                    moves.append(move)

        # move 1 forward
        PAWN_MOVES = (self.WP >> np.uint64(8)) & self.EMPTY 
        PAWN_MOVES_PROMO = (self.WP >> np.uint64(8)) & self.EMPTY & RANK_8

        if not self.isWhiteTurn:
            PAWN_MOVES = (self.BP << np.uint64(8)) & self.EMPTY
            PAWN_MOVES_PROMO = (self.BP << np.uint64(8)) & self.EMPTY & RANK_1

        for i in range(64):
            move = {}
            isPromo = False
            if (PAWN_MOVES_PROMO >> np.uint64(i)) & ONE == ONE:
                move['isPromo'] = True
                move['isWhite'] = self.isWhiteTurn
                isPromo = True
            if (PAWN_MOVES >> np.uint64(i)) & ONE == ONE:
                move['toString'] = makeField((i//8)+(color*1), (i % 8)) + "-"+makeField((i//8), i % 8)
                move['from'] = ((i//8)+(color*1), (i % 8))
                move['to'] = ((i//8), i % 8)
                move['isPawn'] = True
                if isPromo:
                    self.promoHelper(move, moves)
                else:
                    moves.append(move)

        # move 2 forward
        PAWN_MOVES = (self.WP >> np.uint64(16)) & self.EMPTY & RANK_4
    
        if not self.isWhiteTurn:
            PAWN_MOVES = (self.BP << np.uint64(16)) & self.EMPTY & RANK_5

        for i in range(64):
            move = {}
            if (PAWN_MOVES >> np.uint64(i)) & ONE == ONE:
                move['toString'] = makeField((i//8)+(color*2), (i % 8)) + "-"+makeField((i//8), i % 8)
                move['from'] = ((i//8)+(color*2), (i % 8))
                move['to'] = ((i//8), i % 8)
                move['double'] = True
                move['isPawn'] = True
                moves.append(move)

        if self.enPassant != '-':
            RANK = FileMasks8[self.enPassant[0]]

            # en passant right
            PAWN_MOVES = (self.WP << ONE) & self.BP & RANK_5 & ~FILE_A & RANK
            
            if not self.isWhiteTurn:
                PAWN_MOVES = (self.BP >> ONE) & self.WP & RANK_4 & ~FILE_H & RANK
            
            for i in range(64):
                move = {}
                if (PAWN_MOVES >> np.uint64(i)) & ONE == ONE:
                    move['toString'] = makeField((i//8), i % 8-(color*1))+'x'+makeField((i//8)-(color*1), i % 8)
                    move['from'] = ((i//8), i % 8-(color*1))
                    move['to'] = ((i//8)-(color*1), i % 8)
                    move['isPawn'] = True
                    move['enPassant'] = True
                    move['isWhite'] = self.isWhiteTurn

                    moves.append(move)

            # en passant left
            PAWN_MOVES = (self.WP >> ONE) & self.BP & RANK_5 & ~FILE_H & RANK

            if not self.isWhiteTurn:
                PAWN_MOVES = (self.BP << ONE) & self.WP & RANK_4 & ~FILE_A & RANK

            for i in range(64):
                move = {}
                if (PAWN_MOVES >> np.uint64(i)) & ONE == ONE:
                    move['toString'] = makeField((i//8), i % 8+(color*1))+'x'+ makeField((i//8) -(color*1), i % 8)
                    move['from'] = ((i//8), i % 8+(color*1))
                    move['to'] = ((i//8) -(color*1), i % 8)
                    move['isPawn'] = True
                    move['enPassant'] = True
                    move['isWhite'] = self.isWhiteTurn

                    moves.append(move)

        return moves
    
    def promoHelper(self,move, moves):
        if self.isWhiteTurn:
            moveR = copy(move)
            moveR['promoType'] = 'R'
            moves.append(moveR)
            moveQ = copy(move)
            moveQ['promoType'] = 'Q'
            moves.append(moveQ)
            moveB = copy(move)
            moveB['promoType'] = 'B'
            moves.append(moveB)
            moveN = copy(move)
            moveN['promoType'] = 'N'
            moves.append(moveN)
        else:
            moveR = copy(move)
            moveR['promoType'] = 'r'
            moves.append(moveR)
            moveQ = copy(move)
            moveQ['promoType'] = 'q'
            moves.append(moveQ)
            moveB = copy(move)
            moveB['promoType'] = 'b'
            moves.append(moveB)
            moveN = copy(move)
            moveN['promoType'] = 'n'
            moves.append(moveN)

    def HAndVMoves(self, s):
        binaryS = ONE << np.uint64(s)
        possibilitiesHorizontal = (self.OCCUPIED - TWO * binaryS) ^ reverse(reverse(self.OCCUPIED) - TWO * reverse(binaryS))
        possibilitiesVertical = ((self.OCCUPIED & FileMasks82[s % 8]) - (TWO * binaryS)) ^ reverse(reverse(self.OCCUPIED & FileMasks82[s % 8]) - (TWO * reverse(binaryS)))
        return (possibilitiesHorizontal & RankMasks8[(s // 8)]) | (possibilitiesVertical & FileMasks82[s % 8])
    
    def DAndAntiDMoves(self, s:int):
        binaryS =ONE << np.uint64(s)
        possibilitiesDiagonal = ((self.OCCUPIED & DiagonalMasks8[(s // 8) + (s % 8)]) - (TWO * binaryS)) ^ reverse(reverse(self.OCCUPIED & DiagonalMasks8[(s // 8) + (s % 8)]) - (TWO * reverse(binaryS)))
        possibilitiesAntiDiagonal = ((self.OCCUPIED & AntiDiagonalMasks8[(s // 8) + 7 - (s % 8)]) - (TWO * binaryS)) ^ reverse(reverse(self.OCCUPIED & AntiDiagonalMasks8[(s // 8) + 7 - (s % 8)]) - (TWO * reverse(binaryS)))
        return (possibilitiesDiagonal & DiagonalMasks8[(s // 8) + (s % 8)]) | (possibilitiesAntiDiagonal & AntiDiagonalMasks8[(s // 8) + 7 - (s % 8)])
    
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
                move['from'] = ((iLocation//8),iLocation%8)
                move['to'] = ((index//8),index%8)
                move['isPawn'] = False
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
                move['from'] = ((iLocation//8),iLocation%8)
                move['to'] = ((index//8),index%8)
                move['isPawn'] = False
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
                move['from'] = ((iLocation//8),iLocation%8)
                move['to'] = ((index//8),index%8)
                move['isPawn'] = False
                moves.append(move)
                possibility&=~j
                j = possibility & ~(possibility - ONE)
            Q &= ~i
            i = Q&~(Q - ONE)
        return moves
    
    def getMovesN(self, N):    
        moves = []
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
                move['from'] = ((iLoc//8),iLoc%8)
                move['to'] = ((index//8),index%8)
                move['isPawn'] = False
                moves.append(move)
                possibility&=~j
                j=possibility&~(possibility- ONE)
            N &=~i
            i = N &~(N - ONE)
        return moves
    
    def getMovesK(self, K):
        moves = []
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
        while j != 0:
            if j & safe != 0: #filters out unsafe fields
                index = trailingZeros(j) 
                move = {}
                move['toString'] = "K"+makeField((iLoc//8),iLoc%8)+'-'+makeField((index//8),index%8)
                move['from'] = ((iLoc//8),iLoc%8)
                move['to'] = ((index//8),index%8)
                move['isPawn'] = False
                moves.append(move)
            possibility&=~j
            j=possibility&~(possibility- ONE)
        return moves
    
    # TODO Feldern zwischen rochierenden Turm und König müssen leer sein
    # TODO König darf nicht im Schach sein
    # TODO Zielfeld des königs und weg des könig nicht dürfen nicht angegriffen sein
    def getCastleFor(self, isForWhite):
        if isForWhite:
            shift = 0
            R = self.WR
            row = 0
        else:
            shift = 2
            R = self.BR
            row = 7
        moves=[]
        if self.castleRight2[0+shift] and ((ONE<<np.uint64(CASTLE_ROOKS[0+shift])) & R)!=0:
            moves.append({
                'toString':'K'+makeField(row,4)+'-'+makeField(row,6),
                'isHit': False
            })
        if self.castleRight2[1+shift] and ((ONE<<np.uint64(CASTLE_ROOKS[1+shift])) & R)!=0:
            moves.append({
                'toString':'K'+makeField(row,4)+'-'+makeField(row,2),
                'isHit': False
            })
        return moves
        
    
    def unsafeFor(self, isForWhite):
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
            possibility = self.DAndAntiDMoves(iLoc)
            unsafe |= possibility
            QB&=~i
            i=QB&~(QB-ONE)
            
        #staight sliding pieces (rook & queen)
        i = QR &~(QR-ONE)
        while i != 0:
            iLoc = trailingZeros(i)
            possibility = self.HAndVMoves(iLoc)
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

    def makeMove(self, board, move, type) :
        #'regular' move
        if(getattr(move, 'isPromo', False) and getattr(move, 'enPassant', False)):
            start=np.uint64((move['from'][0]*8)+move["from"][1])
            end=np.uint64((move['to'][0]*8)+move['to'][1])
            if (((board>>start)&ONE)==ONE):
                board&=~(ONE<<start)
                board|=(ONE<<end)
            else :
                board&=~(ONE<<end)
        #pawn promotion
        elif (move['isPromo']):
            if (move['isWhite']):
                start=np.uint64(trailingZeros(FileMasks82[move['from'][0] + move['from'][1]]&RankMasks8[7]))
                end=np.uint64(trailingZeros(FileMasks82[move['to'][0] + move['to'][1]]&RankMasks8[6]))
            else:
                start=np.uint64(trailingZeros(FileMasks82[move['from'][0] + move['from'][1]]&RankMasks8[6]))
                end=np.uint64(trailingZeros(FileMasks82[move['to'][0] + move['to'][1]]&RankMasks8[7]))
            
            if (type==move['promoType']):
                board|=(ONE<<end) 
            else:
                board&=~(ONE<<start)
                board&=~(ONE<<end)
        #en passant
        elif (move['enPassant']):
            if (move['isWhite']):
                start=np.uint64(trailingZeros(FileMasks82[move['from'][0] + move['from'][1]]&RankMasks8[3]))
                end=np.uint64(trailingZeros(FileMasks82[move['to'][0] + move['to'][1]]&RankMasks8[2]))
                board&=~(FileMasks82[move['to'][0] + move['to'][1]]&RankMasks8[3])
            else:
                start=np.uint64(trailingZeros(FileMasks82[move['from'][0] + move['from'][1]]&RankMasks8[4]))
                end=np.uint64(trailingZeros(FileMasks82[move['to'][0] + move['to'][1]]&RankMasks8[5]))
                board&=~(FileMasks82[move['to'][0] + move['to'][1]]&RankMasks8[4])
            
            if (((board>>start)&ONE)==ONE):
                board&=~(ONE<<start)
                board|=(ONE<<end)
        else :
            print("ERROR: Invalid move type")
        
        return board
  
# //////////////////
#
#       Tests
#
# ///////////////////
    
b = Board('rnbqkbnr/p6p/1p4p1/2p5/3p1p2/4p3/PPPPPPPP/RNBQKBNR b KQkq - 0 1')
print((b.getMoves()))
