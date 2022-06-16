from moves import *
import numpy as np
from utils import *
import random


blackPromotions = np.uint64(18374686479671623680)
whitePromotions = np.uint64(255)
castleBoards = np.array([9223372036854775808,72057594037927936,128,1],dtype=np.uint64)
possibleCastles = np.array([1,2,4,8],dtype=np.uint8)
zobTable = [[random.randint(1,2**64 - 1) for i in range(12)]for j in range(64)]


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
    hash = 0
    moves = []
    pieceBitboards = np.zeros(shape=6,dtype=np.uint64)
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
        self.moves = []
        self.hash = self.getHash()
        self.updateBitboard()
    
    def updateBitboard(self):
        self.pieceBitboards[0] = np.bitwise_or.reduce(self.pieceList[0])
        self.pieceBitboards[1] = np.bitwise_or.reduce(self.pieceList[1])
        self.pieceBitboards[2] = np.bitwise_or.reduce(self.pieceList[2])
        self.pieceBitboards[3] = np.bitwise_or.reduce(self.pieceList[3])
        self.pieceBitboards[4] = np.bitwise_or.reduce(self.pieceList[4])
        self.pieceBitboards[5] = np.bitwise_or.reduce(self.pieceList[5])

    def getMoves(self):
        self.moves = []
        color = self.white
        enemy = self.black
        if not self.isWhite:
            color = self.black
            enemy = self.white
        allPinned = np.uint64(0)
        allPinned = pinned(self,color,enemy)
        checkFilter = np.uint64((1<<64)-1)
        attacker = inCheck(self,color,enemy,self.isWhite,self.all)
        if attacker:
            checkFilter = attacker
        self.getRookMoves(color,enemy,allPinned,checkFilter)
        self.getBishopMoves(color,enemy,allPinned,checkFilter)
        self.getPawnMoves(color,enemy,allPinned,checkFilter)
        self.getKnightMoves(color,allPinned,checkFilter)
        self.getKingMoves(color,enemy)
        self.getQueenMoves(color,enemy,allPinned,checkFilter)
        return self.moves
       
    def getPawnMoves(self,color,enemy,allPinned,checkFilter):
        if self.isWhite:
            for n in nonzeroElements(self.pieceList[0] & color):
                pieceFieldNumber = np.max(toNumber(n))
                possibleMoves = allMoves[1][pieceFieldNumber][1][0]
                possibleCatches = allMoves[1][pieceFieldNumber][1][1]
                catches = (possibleCatches & (enemy | self.en_passant))
                shadowPieces = np.bitwise_or.reduce(possibleMoves & self.all)
                newMoves = np.append((possibleMoves & ~shadowPieces & ~(shadowPieces>>np.uint64(8))), catches) & checkFilter
                if np.any(newMoves):
                    newMoves = nonzeroElements(newMoves)
                    if np.any(allPinned & n):
                        king = np.max(color & self.pieceList[5])
                        kingNumber = np.max(toNumber(king))
                        for i in nonzeroElements(newMoves):
                            if (between[pieceFieldNumber][kingNumber] & i) or (between[kingNumber][toNumber(i)] & n):
                                self.moves.append((n,i,0,(n>>np.uint64(16)==i),np.uint64(0),np.uint64(0)))
                    else:
                        promotions = nonzeroElements(newMoves & whitePromotions)
                        for i in promotions:
                            x = 1
                            while x < 5:
                                self.moves.append((n,i,0,False,False,x))
                                x += 1
                        newMoves = nonzeroElements(newMoves & ~np.bitwise_or.reduce(promotions))
                        for i in newMoves:
                            all = self.all & ~(n | (i << np.uint64(8)))
                            if not (self.en_passant & i) or not inCheck(self,color,enemy,self.isWhite,all):
                                self.moves.append((n,i,0,(n>>np.uint64(16)==i),np.uint64(0),np.uint64(0)))
        else:
            for n in nonzeroElements(self.pieceList[0] & color):
                pieceFieldNumber = np.max(toNumber(n))
                possibleMoves = allMoves[0][pieceFieldNumber][1][0]
                possibleCatches = allMoves[0][pieceFieldNumber][1][1]
                catches = (possibleCatches & (enemy | self.en_passant))
                shadowPieces = np.bitwise_or.reduce(possibleMoves & self.all)
                newMoves = np.append((possibleMoves & ~shadowPieces & ~(shadowPieces<<np.uint64(8))), catches) & checkFilter
                if np.any(newMoves):
                    newMoves = nonzeroElements(newMoves)
                    if np.any(allPinned & n):
                        king = np.max(color & self.pieceList[5])
                        kingNumber = np.max(toNumber(king))
                        for i in nonzeroElements(newMoves):
                            if (between[pieceFieldNumber][kingNumber] & i) or (between[kingNumber][toNumber(i)] & n):
                                self.moves.append((n,i,0,(n<<np.uint64(16)==i),np.uint64(0),np.uint64(0)))
                    else:
                        promotions = nonzeroElements(newMoves & whitePromotions)
                        for i in promotions:
                            x = 1
                            while x < 5:
                                self.moves.append((n,i,0,False,np.uint64(0),x))
                                x += 1
                        newMoves = nonzeroElements(newMoves & ~np.bitwise_or.reduce(promotions))
                        for i in newMoves:
                            all = self.all & ~(n | (i >> np.uint64(8)))
                            if not (self.en_passant & i) or not inCheck(self,color,enemy,self.isWhite,all):
                                self.moves.append((n,i,0,(n<<np.uint64(16)==i),np.uint64(0),np.uint64(0)))

    def getRookMoves(self,color,enemy,allPinned,checkFilter):
        for n in nonzeroElements(self.pieceList[1] & color):
            pieceFieldNumber = np.max(toNumber(n))
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
                        kingNumber = np.max(toNumber(king))
                        for i in newMoves:
                            if (between[pieceFieldNumber][kingNumber] & i) or (between[kingNumber][toNumber(i)] & n):
                                self.moves.append((n,i,1,False,np.uint64(0),np.uint64(0)))
                else:
                    for i in newMoves:
                        self.moves.append((n,i,1,False,np.uint64(0),np.uint64(0)))

    def getBishopMoves(self,color,enemy,allPinned,checkFilter):
        for n in nonzeroElements(self.pieceList[3] & color):
            pieceFieldNumber = np.max(toNumber(n))
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
                        kingNumber = np.max(toNumber(king))
                        for i in newMoves:
                            if (between[pieceFieldNumber][kingNumber] & i) or (between[kingNumber][toNumber(i)] & n):
                                self.moves.append((n,i,3,False,np.uint64(0),np.uint64(0)))
                else:
                    for i in newMoves:
                        self.moves.append((n,i,3,False,np.uint64(0),np.uint64(0)))

    def getKnightMoves(self,color,allPinned,checkFilter):
        for n in nonzeroElements(self.pieceList[2] & color):
            pieceFieldNumber = np.max(toNumber(n))
            possibleMoves = allMoves[5][pieceFieldNumber][1]
            shadowPieces = np.bitwise_or.reduce(possibleMoves & color)
            newMoves = (possibleMoves & ~shadowPieces) & checkFilter
            if np.any(newMoves):
                newMoves = nonzeroElements(newMoves)
                if allPinned & n:
                        king = nonzeroElements(color & self.pieceList[5])
                        kingNumber = np.max(toNumber(king))
                        for i in newMoves:
                            if (between[pieceFieldNumber][kingNumber] & i) or (between[kingNumber][toNumber(i)] & n):
                                self.moves.append((n,i,2,False,np.uint64(0),np.uint64(0)))
                else:
                    for i in newMoves:
                        self.moves.append((n,i,2,False,np.uint64(0),np.uint64(0)))
    
    def getKingMoves(self,color,enemy):
        for n in nonzeroElements(self.pieceList[5] & color):
            pieceFieldNumber = np.max(toNumber(n))
            possibleMoves = allMoves[4][pieceFieldNumber][1]
            shadowPieces = np.bitwise_or.reduce(possibleMoves & color)
            newMoves = (possibleMoves & ~shadowPieces)
            if np.any(newMoves):
                for i in nonzeroElements(newMoves):
                    all = self.all & ~n
                    if not attacked(self,enemy,self.isWhite,i,all):
                        self.moves.append((n,i,5,False,np.uint64(0),np.uint64(0)))
            if self.castle:
                if not attacked(self,enemy,self.isWhite,n,self.all):
                    if (self.isWhite and (self.castle & 1)) or (not self.isWhite and (self.castle & 4)):
                        if not (n << np.uint64(1) & self.all) and not (n << np.uint64(2) & self.all) and not attacked(self,enemy,self.isWhite,n << np.uint64(1),self.all) and not attacked(self,enemy,self.isWhite,n << np.uint64(2),self.all):
                            if self.isWhite:
                                self.moves.append((n,n << np.uint64(2),5,False,np.uint64(1),np.uint64(0)))
                            else:
                                self.moves.append((n,n << np.uint64(2),5,False,np.uint64(2),np.uint64(0)))
                    if (self.isWhite and (self.castle & 2)) or (not self.isWhite and (self.castle & 8)):
                        if not (n >> np.uint64(1) & self.all) and not (n >> np.uint64(2) & self.all) and not (n >> np.uint64(3) & self.all) and not attacked(self,enemy,self.isWhite,n >> np.uint64(1),self.all) and not attacked(self,enemy,self.isWhite,n >> np.uint64(2),self.all):
                            if self.isWhite:
                                self.moves.append((n,n >> np.uint64(2),5,False,np.uint64(4),np.uint64(0)))
                            else:
                                self.moves.append((n,n >> np.uint64(2),5,False,np.uint64(8),np.uint64(0)))
    
    def getQueenMoves(self,color,enemy,allPinned,checkFilter):
        for n in nonzeroElements(self.pieceList[4] & color):
            pieceFieldNumber = np.max(toNumber(n))
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
                        kingNumber = np.max(toNumber(king))
                        for i in newMoves:
                            if (between[pieceFieldNumber][kingNumber] & i) or (between[kingNumber][toNumber(i)] & n):
                                self.moves.append((n,i,4,False,np.uint64(0),np.uint64(0)))
                else:
                    for i in newMoves:
                        self.moves.append((n,i,4,False,np.uint64(0),np.uint64(0)))
        for n in nonzeroElements(self.pieceList[4] & color):
            pieceFieldNumber = np.max(toNumber(n))
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
                        kingNumber = np.max(toNumber(king))
                        for i in newMoves:
                            if (between[pieceFieldNumber][kingNumber] & i) or (between[kingNumber][toNumber(i)] & n):
                                self.moves.append((n,i,4,False,np.uint64(0),np.uint64(0)))
                else:
                    for i in newMoves:
                        self.moves.append((n,i,4,False,np.uint64(0),np.uint64(0)))
    
    def doMove(self, move, persistant = False):
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
        zobTablePieceNumber = 0
        if not self.isWhite:
            zobTablePieceNumber = 6
        if self.pieceBitboards[0] & toField:
            catch = 0
            self.pieceList[0] = nonzeroElements(self.pieceList[0] & ~toField)
            self.hash ^= zobTable[toNumber(toField)][(zobTablePieceNumber+6)%12]
        elif self.pieceBitboards[1] & toField:
            catch = 1
            self.pieceList[1] = nonzeroElements(self.pieceList[1] & ~toField)
            self.hash ^= zobTable[toNumber(toField)][(zobTablePieceNumber+7)%12]
        elif self.pieceBitboards[2] & toField:
            catch = 2
            self.pieceList[2] = nonzeroElements(self.pieceList[2] & ~toField)
            self.hash ^= zobTable[toNumber(toField)][(zobTablePieceNumber+8)%12]
        elif self.pieceBitboards[3] & toField:
            catch = 3
            self.pieceList[3] = nonzeroElements(self.pieceList[3] & ~toField)
            self.hash ^= zobTable[toNumber(toField)][(zobTablePieceNumber+9)%12]
        elif self.pieceBitboards[4] & toField:
            catch = 4
            self.pieceList[4] = nonzeroElements(self.pieceList[4] & ~toField)
            self.hash ^= zobTable[toNumber(toField)][(zobTablePieceNumber+10)%12]

        self.pieceList[piece] = nonzeroElements(self.pieceList[piece] & ~fromField)
        self.hash ^= zobTable[toNumber(fromField)][zobTablePieceNumber+piece]

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
                self.hash ^= zobTable[toNumber(toField)][zobTablePieceNumber+promotion]
            elif en_passant:
                if self.isWhite:
                    self.en_passant = fromField>>np.uint64(8)
                else:
                    self.en_passant = fromField<<np.uint64(8)
                self.pieceList[0] = nonzeroElements(self.pieceList[0] & ~toField)
                self.hash ^= zobTable[toNumber(toField)][(zobTablePieceNumber+6)%12]
                self.pieceList[0] = np.append(self.pieceList[0], toField)
                self.hash ^= zobTable[toNumber(toField)][zobTablePieceNumber]
            else:
                if toField & oldEnPassant:
                    catch = 0
                    self.pieceList[0] = nonzeroElements(self.pieceList[0]& ~(oldEnPassant))  
                    self.hash ^= zobTable[toNumber(oldEnPassant)][zobTablePieceNumber]
                    self.all = self.all & ~oldEnPassant
                    if self.isWhite:
                        self.black = self.black & ~oldEnPassant
                    else:
                        self.white = self.white & ~oldEnPassant
                self.pieceList[0] = np.append(self.pieceList[0], toField)
                self.hash ^= zobTable[toNumber(toField)][zobTablePieceNumber]
        else:
            self.pieceList[piece] = np.append(self.pieceList[piece], toField)
            self.hash ^= zobTable[toNumber(toField)][zobTablePieceNumber+piece]
            if piece == 1:
                possibleCastle = fromField & castleBoards
                if np.any(possibleCastle):
                    self.castle &= ~possibleCastles[np.nonzero(possibleCastle)]
            elif castle:
                if castle & np.uint(1):
                    castleRookTo = np.uint64(1 << 61)
                    castleRookFrom = np.uint64(1 << 63)
                    self.castle &= ~np.uint(3)
                elif castle & np.uint(4):
                    castleRookTo = np.uint64(1 << 5)
                    castleRookFrom = np.uint64(1 << 7)
                    self.castle &= ~np.uint(12)
                elif castle & np.uint(2):
                    castleRookTo = np.uint64(1 << 59)
                    castleRookFrom = np.uint64(1 << 56)
                    self.castle &= ~np.uint(3)
                else:
                    castleRookTo = np.uint64(1 << 3)
                    castleRookFrom = np.uint64(1 << 1)
                    self.castle &= ~np.uint(12)
                self.pieceList[1] = nonzeroElements(np.append(self.pieceList[1], castleRookTo) & ~castleRookFrom)
                self.hash ^= zobTable[toNumber(castleRookTo)][zobTablePieceNumber+1]
                self.hash ^= zobTable[toNumber(castleRookFrom)][zobTablePieceNumber+1]
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
        
        self.updateBitboard()
        self.moves = []
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
        self.isWhite = not self.isWhite

        self.pieceList[piece] = np.append(nonzeroElements(self.pieceList[piece] & ~toField),fromField)

        if self.isWhite:
            EnPassant = self.en_passant<<np.uint64(8)
        else:
            EnPassant = self.en_passant>>np.uint64(8)

        if promotion:
            self.pieceList[promotion] = nonzeroElements(self.pieceList[promotion] & ~toField)
            if self.isWhite:
                self.hash ^= zobTable[toNumber(toField)][promotion]
            else:
                self.hash ^= zobTable[toNumber(toField)][promotion+6]

        if catch == 0 and EnPassant & toField:
            self.pieceList[catch] = np.append(self.pieceList[catch], self.en_passant)
            if self.isWhite:
                self.black |= EnPassant
                self.hash ^= zobTable[toNumber(EnPassant)][catch+6]
            else:
                self.white |= EnPassant
                self.hash ^= zobTable[toNumber(EnPassant)][catch]
        elif (catch >= 0):
            self.pieceList[catch] = np.append(self.pieceList[catch], toField)
            if self.isWhite:
                self.black |= toField
                self.hash ^= zobTable[toNumber(toField)][catch+6]
            else:
                self.white |= toField
                self.hash ^= zobTable[toNumber(toField)][catch]

        if castle:
            self.pieceList[1] = np.append(nonzeroElements(self.pieceList[1] & ~castleRookTo),castleRookFrom)
            if self.isWhite:
                self.white = (self.white | castleRookFrom) & ~castleRookTo
                self.hash ^= zobTable[toNumber(castleRookFrom)][1]
                self.hash ^= zobTable[toNumber(castleRookTo)][1]
            else:
                self.black = (self.black | castleRookFrom) & ~castleRookTo
                self.hash ^= zobTable[toNumber(castleRookFrom)][7]
                self.hash ^= zobTable[toNumber(castleRookTo)][7]

        self.updateBitboard()
        if self.isWhite:
            self.white = (self.white | fromField) & ~toField
        else:
            self.black = (self.black | fromField) & ~toField
        self.all = self.white | self.black

        if self.isWhite and not promotion:
            self.hash ^= zobTable[toNumber(fromField)][piece]
            self.hash ^= zobTable[toNumber(toField)][piece]
        elif not promotion:
            self.hash ^= zobTable[toNumber(fromField)][piece+6]
            self.hash ^= zobTable[toNumber(toField)][piece+6]

        self.moves = []
        return self

    def undoAllMoves(self):
        while len(self.moveHistoryAB) > 0:
            move = self.moveHistoryAB.pop()
            self.undoMove(move)

    def undoLastMove(self):
        if len(self.moveHistoryAB) > 0:
            move = self.moveHistoryAB.pop()
            self.undoMove(move)
    
    def deepcopy(self):
        return Board(toFen(self))

    def getHash(self):
        hash = 0
        for x in range(6):
            whitePieces = self.pieceList[x] & self.white
            for y in nonzeroElements(whitePieces):
                hash ^= zobTable[toNumber(y)][x]
            blackPieces = self.pieceList[x] & self.black
            for y in nonzeroElements(blackPieces):
                hash ^= zobTable[toNumber(y)][x+6]
        ##for i in range(8):
        ##    for j in range(8):
        ##        if board[i][j] != '-':
        ##            piece = self.indexing(board[i][j])
        ##            hash ^= zobTable[i][j][piece]
        return hash

    def getEntry(self):
        return self.ttable.get(self.getHash())


def getFen(fen):
    self = Board(fen)
    self.getMoves()
    self.doMove(self.moves[0])
    return toFen(self) ##toFen(doMove(self,moves[0][0],moves[0][1],moves[0][2],moves[0][3],moves[0][4],moves[0][5]))
