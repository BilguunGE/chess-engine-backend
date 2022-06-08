from moves import *
import numpy as np
from utils import *
import random

whitePromotions = np.uint64(18374686479671623680)
blackPromotions = np.uint64(255)
castleBoards = np.array([9223372036854775808,72057594037927936,128,1],dtype=np.uint64)
possibleCastles = np.array([1,2,4,8],dtype=np.uint8)
zobTable = [[[random.randint(1,2**64 - 1) for i in range(12)]for j in range(8)]for k in range(8)]

max = 'w'

class Board:
    all = np.uint64(0)
    ##pieceNr == 0-Pawn, 1-Rook, 2-Knight, 3-Bishop, 4-Queen, 5-King
    pieceList = [np.array([], dtype=np.uint64)]*6
    white = np.uint64(0)
    black = np.uint64(0)
    castle = np.uint8(0)
    en_passant = np.uint64(0)
    halfmove = 0
    fullmove = 1
    isWhite = True
    moveHistoryAB = []
    ttable = {}

    def __init__(self,fenString):
        fen = fenString.split()
        fenArray = fen[0].split('/')
        x = 0
        for i in fenArray:
            for j in i:
                if j >= '0' and j <= '9':
                    x += int(j)
                else:
                    z = 1 << x
                    self.all |= np.uint64(z)
                    if j.isupper():
                        self.white |= np.uint64(z)
                    else:
                        self.black |= np.uint64(z)
                    if j == 'p' or j == 'P':
                        self.pieceList[0] = np.append(self.pieceList[0], np.uint64(z))
                    elif j == 'r' or j == 'R':
                        self.pieceList[1] = np.append(self.pieceList[1], np.uint64(z))
                    elif j == 'n' or j == 'N':
                        self.pieceList[2] = np.append(self.pieceList[2], np.uint64(z))
                    elif j == 'b' or j == 'B':
                        self.pieceList[3] = np.append(self.pieceList[3], np.uint64(z))
                    elif j == 'q' or j == 'Q':
                        self.pieceList[4] = np.append(self.pieceList[4], np.uint64(z))
                    elif j == 'k' or j == 'K':
                        self.pieceList[5] = np.append(self.pieceList[5], np.uint64(z))
                    x += 1

        for i in fen[2]:
            if i == 'K':
                self.castle |= np.uint8(1)
            if i == 'Q':
                self.castle |= np.uint8(2)
            if i == 'k':
                self.castle |= np.uint8(4)
            if i == 'q':
                self.castle |= np.uint8(8)

        if fen[3] != '-':
            x = 8-int(fen[3][1])
            y = ord(fen[3][0]) - 97
            self.en_passant |= np.uint64(1 << (x*8+y))
    
        self.isWhite = fen[1] == 'w'
        self.halfmove = int(fen[4])
        self.fullmove = int(fen[5])
    
    def getMoves(self):
        color = self.white
        enemy = self.black
        if not self.isWhite:
            color = self.black
            enemy = self.white
        moves = []
        allPinned = np.uint64(0)
        allPinned = pinned(self,color,enemy)
        checkFilter = np.uint64((1<<64)-1)
        attacker = inCheck(self,color,enemy,self.isWhite)
        if attacker:
            checkFilter = attacker
        moves.extend(self.getRookMoves(color,enemy,allPinned,checkFilter))
        moves.extend(self.getBishopMoves(color,enemy,allPinned,checkFilter))
        moves.extend(self.getPawnMoves(color,enemy,allPinned,checkFilter))
        moves.extend(self.getKnightMoves(color,allPinned,checkFilter))
        moves.extend(self.getKingMoves(color,enemy))
        moves.extend(self.getQueenMoves(color,enemy,allPinned,checkFilter))
        return moves
       
    def getPawnMoves(self,color,enemy,allPinned,checkFilter):
        moves = []
        if self.isWhite:
            for n in nonzeroElements(self.pieceList[0] & color):
                pieceFieldNumber = toNumber(n)
                possibleMoves = allMoves[1][pieceFieldNumber][1][0]
                possibleCatches = allMoves[1][pieceFieldNumber][1][1]
                catches = (possibleCatches & (enemy | self.en_passant))
                shadowPieces = np.bitwise_or.reduce(possibleMoves & self.all)
                newMoves = np.append((possibleMoves & ~shadowPieces & ~(shadowPieces>>np.uint64(8))), catches) & checkFilter
                if np.any(newMoves):
                    newMoves = nonzeroElements(newMoves)
                    if np.any(allPinned & n):
                        king = np.max(color & self.pieceList[5])
                        kingNumber = toNumber(king)
                        for i in nonzeroElements(newMoves):
                            if (between[pieceFieldNumber][kingNumber] & i) or (between[kingNumber][toNumber(i)] & n):
                                moves.append((n,i,0,(n>>np.uint64(16)==i),np.uint64(0),np.uint64(0)))
                    else:
                        promotions = nonzeroElements(newMoves & whitePromotions)
                        for i in promotions:
                            x = 1
                            while x < 5:
                                moves.append((n,i,0,False,False,x))
                                x += 1
                        newMoves = nonzeroElements(newMoves & ~np.bitwise_or.reduce(promotions))
                        for i in newMoves:
                            all = self.all & ~(n | (i << np.uint64(8)))
                            if not (self.en_passant & i) or not inCheck(self,color,enemy,self.isWhite,all):
                                moves.append((n,i,0,(n>>np.uint64(16)==i),np.uint64(0),np.uint64(0)))
        else:
            for n in nonzeroElements(self.pieceList[0] & color):
                pieceFieldNumber = toNumber(n)
                possibleMoves = allMoves[0][pieceFieldNumber][1][0]
                possibleCatches = allMoves[0][pieceFieldNumber][1][1]
                catches = (possibleCatches & (enemy | self.en_passant))
                shadowPieces = np.bitwise_or.reduce(possibleMoves & self.all)
                newMoves = np.append((possibleMoves & ~shadowPieces & ~(shadowPieces<<np.uint64(8))), catches) & checkFilter
                if np.any(newMoves):
                    newMoves = nonzeroElements(newMoves)
                    if np.any(allPinned & n):
                        king = np.max(color & self.pieceList[5])
                        kingNumber = toNumber(king)
                        for i in nonzeroElements(newMoves):
                            if (between[pieceFieldNumber][kingNumber] & i) or (between[kingNumber][toNumber(i)] & n):
                                moves.append((n,i,0,(n<<np.uint64(16)==i),np.uint64(0),np.uint64(0)))
                    else:
                        promotions = nonzeroElements(newMoves & whitePromotions)
                        for i in promotions:
                            x = 1
                            while x < 5:
                                moves.append((n,i,0,False,np.uint64(0),x))
                                x += 1
                        newMoves = nonzeroElements(newMoves & ~np.bitwise_or.reduce(promotions))
                        for i in newMoves:
                            all = self.all & ~(n | (i >> np.uint64(8)))
                            if not (self.en_passant & i) or not inCheck(self,color,enemy,self.isWhite,all):
                                moves.append((n,i,0,(n<<np.uint64(16)==i),np.uint64(0),np.uint64(0)))
        return moves

    def getRookMoves(self,color,enemy,allPinned,checkFilter):
        moves = []
        for n in nonzeroElements(self.pieceList[1] & color):
            pieceFieldNumber = toNumber(n)
            possibleMoves = allMoves[2][pieceFieldNumber][1]
            colorShadowPieces = nonzeroElements(possibleMoves & color)
            colorShadows = np.uint64(0)
            if np.any(colorShadowPieces):
                colorShadows = np.bitwise_or.reduce(allShadows[0][pieceFieldNumber][toNumber(colorShadowPieces)])
            newMoves = (possibleMoves & ~(colorShadows | np.bitwise_or.reduce(colorShadowPieces))) & checkFilter
            if np.any(newMoves):
                enemyShadowPieces = nonzeroElements(newMoves & enemy)
                enemyShadows = np.uint64(0)
                if np.any(enemyShadowPieces):
                    enemyShadows = np.bitwise_or.reduce(allShadows[0][pieceFieldNumber][toNumber(enemyShadowPieces)])
                newMoves &= ~enemyShadows
                newMoves = nonzeroElements(newMoves)
                if allPinned & n:
                        king = nonzeroElements(color & self.pieceList[5])
                        kingNumber = toNumber(king)
                        for i in newMoves:
                            if (between[pieceFieldNumber][kingNumber] & i) or (between[kingNumber][toNumber(i)] & n):
                                moves.append((n,i,1,False,np.uint64(0),np.uint64(0)))
                else:
                    for i in newMoves:
                        moves.append((n,i,1,False,np.uint64(0),np.uint64(0)))
        return moves

    def getBishopMoves(self,color,enemy,allPinned,checkFilter):
        moves = []
        for n in nonzeroElements(self.pieceList[3] & color):
            pieceFieldNumber = toNumber(n)
            possibleMoves = allMoves[3][pieceFieldNumber][1]
            colorShadowPieces = nonzeroElements(possibleMoves & color)
            colorShadows = np.uint64(0)
            if np.any(colorShadowPieces):
                colorShadows = np.bitwise_or.reduce(allShadows[1][pieceFieldNumber][toNumber(colorShadowPieces)])
            newMoves = (possibleMoves & ~(colorShadows | np.bitwise_or.reduce(colorShadowPieces))) & checkFilter
            if np.any(newMoves):
                enemyShadowPieces = nonzeroElements(newMoves & enemy)
                enemyShadows = np.uint64(0)
                if np.any(enemyShadowPieces):
                    enemyShadows = np.bitwise_or.reduce(allShadows[1][pieceFieldNumber][toNumber(enemyShadowPieces)])
                newMoves &= ~enemyShadows
                newMoves = nonzeroElements(newMoves)
                if allPinned & n:
                        king = nonzeroElements(color & self.pieceList[5])
                        kingNumber = toNumber(king)
                        for i in newMoves:
                            if (between[pieceFieldNumber][kingNumber] & i) or (between[kingNumber][toNumber(i)] & n):
                                moves.append((n,i,3,False,np.uint64(0),np.uint64(0)))
                else:
                    for i in newMoves:
                        moves.append((n,i,3,False,np.uint64(0),np.uint64(0)))
        return moves
    def getKnightMoves(self,color,allPinned,checkFilter):
        moves = []
        for n in nonzeroElements(self.pieceList[2] & color):
            pieceFieldNumber = toNumber(n)
            possibleMoves = allMoves[5][pieceFieldNumber][1]
            shadowPieces = np.bitwise_or.reduce(possibleMoves & color)
            newMoves = (possibleMoves & ~shadowPieces) & checkFilter
            if np.any(newMoves):
                newMoves = nonzeroElements(newMoves)
                if allPinned & n:
                        king = nonzeroElements(color & self.pieceList[5])
                        kingNumber = toNumber(king)
                        for i in newMoves:
                            if (between[pieceFieldNumber][kingNumber] & i) or (between[kingNumber][toNumber(i)] & n):
                                moves.append((n,i,2,False,np.uint64(0),np.uint64(0)))
                else:
                    for i in newMoves:
                        moves.append((n,i,2,False,np.uint64(0),np.uint64(0)))
        return moves
    
    def getKingMoves(self,color,enemy):
        moves = []
        for n in nonzeroElements(self.pieceList[5] & color):
            pieceFieldNumber = toNumber(n)
            possibleMoves = allMoves[4][pieceFieldNumber][1]
            shadowPieces = np.bitwise_or.reduce(possibleMoves & color)
            newMoves = (possibleMoves & ~shadowPieces)
            if np.any(newMoves):
                for i in nonzeroElements(newMoves):
                    all = self.all & ~n
                    if not attacked(self,enemy,self.isWhite,i,all):
                        moves.append((n,i,5,False,np.uint64(0),np.uint64(0)))
            if self.castle:
                if not attacked(self,enemy,self.isWhite,n,self.all):
                    if (self.isWhite and (self.castle & 1)) or (not self.isWhite and (self.castle & 4)):
                        if not (n << np.uint64(1) & self.all) and not (n << np.uint64(2) & self.all) and not attacked(self,enemy,self.isWhite,n << np.uint64(1),self.all) and not attacked(self,enemy,self.isWhite,n << np.uint64(2),self.all):
                            if self.isWhite:
                                moves.append((n,n << np.uint64(2),5,False,np.uint64(1),np.uint64(0)))
                            else:
                                moves.append((n,n << np.uint64(2),5,False,np.uint64(2),np.uint64(0)))
                    if (self.isWhite and (self.castle & 2)) or (not self.isWhite and (self.castle & 8)):
                        if not (n >> np.uint64(1) & self.all) and not (n >> np.uint64(2) & self.all) and not (n >> np.uint64(3) & self.all) and not attacked(self,enemy,self.isWhite,n >> np.uint64(1),self.all) and not attacked(self,enemy,self.isWhite,n >> np.uint64(2),self.all):
                            if self.isWhite:
                                moves.append((n,n >> np.uint64(2),5,False,np.uint64(4),np.uint64(0)))
                            else:
                                moves.append((n,n >> np.uint64(2),5,False,np.uint64(8),np.uint64(0)))
        return moves
    
    def getQueenMoves(self,color,enemy,allPinned,checkFilter):
        moves = []
        for n in nonzeroElements(self.pieceList[4] & color):
            pieceFieldNumber = toNumber(n)
            possibleMoves = allMoves[2][pieceFieldNumber][1]
            colorShadowPieces = nonzeroElements(possibleMoves & color)
            colorShadows = np.uint64(0)
            if np.any(colorShadowPieces):
                colorShadows = np.bitwise_or.reduce(allShadows[0][pieceFieldNumber][toNumber(colorShadowPieces)])
            newMoves = (possibleMoves & ~(colorShadows | np.bitwise_or.reduce(colorShadowPieces))) & checkFilter
            if np.any(newMoves):
                enemyShadowPieces = nonzeroElements(newMoves & enemy)
                enemyShadows = np.uint64(0)
                if np.any(enemyShadowPieces):
                    enemyShadows = np.bitwise_or.reduce(allShadows[0][pieceFieldNumber][toNumber(enemyShadowPieces)])
                newMoves &= ~enemyShadows
                newMoves = nonzeroElements(newMoves)
                if allPinned & n:
                        king = nonzeroElements(color & self.pieceList[5])
                        kingNumber = toNumber(king)
                        for i in newMoves:
                            if (between[pieceFieldNumber][kingNumber] & i) or (between[kingNumber][toNumber(i)] & n):
                                moves.append((n,i,4,False,np.uint64(0),np.uint64(0)))
                else:
                    for i in newMoves:
                        moves.append((n,i,4,False,np.uint64(0),np.uint64(0)))
        for n in nonzeroElements(self.pieceList[4] & color):
            pieceFieldNumber = toNumber(n)
            possibleMoves = allMoves[3][pieceFieldNumber][1]
            colorShadowPieces = nonzeroElements(possibleMoves & color)
            colorShadows = np.uint64(0)
            if np.any(colorShadowPieces):
                colorShadows = np.bitwise_or.reduce(allShadows[1][pieceFieldNumber][toNumber(colorShadowPieces)])
            newMoves = (possibleMoves & ~(colorShadows | np.bitwise_or.reduce(colorShadowPieces))) & checkFilter
            if np.any(newMoves):
                enemyShadowPieces = nonzeroElements(newMoves & enemy)
                enemyShadows = np.uint64(0)
                if np.any(enemyShadowPieces):
                    enemyShadows = np.bitwise_or.reduce(allShadows[1][pieceFieldNumber][toNumber(enemyShadowPieces)])
                newMoves &= ~enemyShadows
                newMoves = nonzeroElements(newMoves)
                if allPinned & n:
                        king = nonzeroElements(color & self.pieceList[5])
                        kingNumber = toNumber(king)
                        for i in newMoves:
                            if (between[pieceFieldNumber][kingNumber] & i) or (between[kingNumber][toNumber(i)] & n):
                                moves.append((n,i,4,False,np.uint64(0),np.uint64(0)))
                else:
                    for i in newMoves:
                        moves.append((n,i,4,False,np.uint64(0),np.uint64(0)))
        return moves
    
    def doMove(self, move, persistant= False):
        ##pieceNr == 0-Pawn, 1-Rook, 2-Knight, 3-Bishop, 4-Queen, 5-King
        fromField = move[0]
        toField = move[1]
        piece = move[2]
        en_passant = move[3]
        castle = move[4]
        promotion = move[5]
        undoEnPassant = self.en_passant
        undoHalfmove = self.halfmove
        undoCastle = self.castle
        catch = -1
        castleRookTo = 0
        castleRookFrom = 0
        if np.any(self.pieceList[0] & toField):
            catch = 0
            self.pieceList[0] = nonzeroElements(self.pieceList[0] & ~toField)
        elif np.any(self.pieceList[1] & toField):
            catch = 1
            self.pieceList[1] = nonzeroElements(self.pieceList[1] & ~toField)
        elif np.any(self.pieceList[2] & toField):
            catch = 2
            self.pieceList[2] = nonzeroElements(self.pieceList[2] & ~toField)
        elif np.any(self.pieceList[3] & toField):
            catch = 3
            self.pieceList[3] = nonzeroElements(self.pieceList[3] & ~toField)
        elif np.any(self.pieceList[4] & toField):
            catch = 4
            self.pieceList[4] = nonzeroElements(self.pieceList[4] & ~toField)

        self.pieceList[piece] = nonzeroElements(self.pieceList[piece] & ~fromField)

        self.all = (self.all | toField) & ~fromField
        self.fullmove += 1
        self.halfmove += 1

        if self.isWhite:
            oldEnPassant = self.en_passant<<np.uint64(8)
        else:
            oldEnPassant = self.en_passant>>np.uint64(8)
        self.en_passant = np.uint64(0)
        if not piece:
            self.halfmove = 0
            if promotion:
                self.pieceList[promotion] = np.append(self.pieceList[promotion], toField)
            elif en_passant:
                if self.isWhite:
                    self.en_passant = fromField>>np.uint64(8)
                else:
                    self.en_passant = fromField<<np.uint64(8)
                self.pieceList[0] = nonzeroElements(self.pieceList[0] & ~toField)
                self.pieceList[0] = np.append(self.pieceList[0], toField)
            else:
                if toField & oldEnPassant:
                    self.pieceList[0] = nonzeroElements(self.pieceList[0]& ~(oldEnPassant))  
                    self.all = self.all & ~oldEnPassant
                    if self.isWhite:
                        self.black = self.black & ~oldEnPassant
                    else:
                        self.white = self.white & ~oldEnPassant
                self.pieceList[0] = np.append(self.pieceList[0], toField)
        else:
            self.pieceList[piece] = np.append(self.pieceList[piece], toField)
            if piece == 1:
                possibleCastle = fromField & castleBoards
                if np.any(possibleCastle):
                    self.castle &= ~possibleCastles[np.nonzero(possibleCastle)]
            elif castle:
                if castle & 1:
                    castleRookTo = np.uint64(1 << 61)
                    castleRookFrom = np.uint64(1 << 63)
                elif castle & 4:
                    castleRookTo = np.uint64(1 << 5)
                    castleRookFrom = np.uint64(1 << 7)
                elif castle & 2:
                    castleRookTo = np.uint64(1 << 59)
                    castleRookFrom = np.uint64(1 << 56)
                else:
                    castleRookTo = np.uint64(1 << 3)
                    castleRookFrom = np.uint64(1 << 1)
                self.pieceList[1] = nonzeroElements(np.append(self.pieceList[1], castleRookTo) & ~castleRookFrom)
                if self.isWhite:
                    self.white = (self.white & ~castleRookFrom) | castleRookTo
                else:
                    self.black = (self.black & ~castleRookFrom) | castleRookTo
                self.all = self.black | self.white
            elif piece == 5:
                if self.isWhite:
                    self.castle &= ~np.uint(3)
                else:
                    self.castle &= ~np.uint(12)
        if self.isWhite:
            if (toField & self.black):
                self.halfmove = 0
            self.black = self.black & ~toField
            self.white = (self.white | toField) & ~fromField
        else:
            if (toField & self.white):
                self.halfmove = 0
            self.white = self.white & ~toField
            self.black = (self.black | toField) & ~fromField
        self.isWhite = not self.isWhite

        if not persistant:
            self.moveHistoryAB.append((move,undoHalfmove,undoCastle,undoEnPassant,catch,castleRookFrom,castleRookTo))

        return self

    def undoMove(self, undoMove):
        move = undoMove[0]
        fromField = move[0]
        toField = move[1]
        piece = move[2]
        castle = move[4]
        promotion = move[5]
        catch = undoMove[4]
        castleRookFrom = undoMove[5]
        castleRookTo = undoMove[6]

        self.halfmove = undoMove[1]
        self.castle = undoMove[2]
        self.en_passant = undoMove[3]
        self.fullmove -= 1

        self.pieceList[piece] = np.append(nonzeroElements(self.pieceList[piece] & ~toField),fromField)

        if promotion:
            self.pieceList[promotion] = nonzeroElements(self.pieceList[promotion] & ~toField)

        if not (catch == -1):
            self.pieceList[catch] = np.append(self.pieceList[catch], toField)

        if castle:
            self.pieceList[1] = np.append(nonzeroElements(self.pieceList[piece] & ~castleRookTo),castleRookFrom)


        return self

    def undoAllMoves(self):
        while len(self.moveHistoryAB) > 0:
            move = self.moveHistoryAB.pop()
            self.undoMove(move)

    def deepcopy(self):
        return Board(toFen(self))
    
    def indexing(self, piece):
    # mapping each piece to a particular number
        if (piece=='P'):
            return 0
        if (piece=='N'):
            return 1
        if (piece=='B'):
            return 2
        if (piece=='R'):
            return 3
        if (piece=='Q'):
            return 4
        if (piece=='K'):
            return 5
        if (piece=='p'):
            return 6
        if (piece=='n'):
            return 7
        if (piece=='b'):
            return 8
        if (piece=='r'):
            return 9
        if (piece=='q'):
            return 10
        if (piece=='k'):
            return 11
        else:
            return -1

    def getHash(self):
        board = [
            ['-', '-', '-', 'K', '-', '-', '-', '-'],
            ['-', 'R', '-', '-', '-', '-', 'Q', '-'],
            ['-', '-', '-', '-', '-', '-', '-', '-'],
            ['-', 'P', '-', '-', '-', '-', 'p', '-'],
            ['-', '-', '-', '-', '-', 'p', '-', '-'],
            ['-', '-', '-', '-', '-', '-', '-', '-'],
            ['p', '-', '-', '-', 'b', '-', '-', 'q'],
            ['-', '-', '-', '-', 'n', '-', '-', 'k']
        ]
        hash = 0
        for i in range(8):
            for j in range(8):
                if board[i][j] != '-':
                    piece = self.indexing(board[i][j])
                    hash ^= zobTable[i][j][piece]
        return hash

    def getEntry(self):
        return self.ttable.get(self.getHash())
