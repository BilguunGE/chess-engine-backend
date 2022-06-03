from moves import *
import numpy as np
from utils import *

whitePromotions = np.uint64(18374686479671623680)
blackPromotions = np.uint64(255)
castleBoards = np.array([9223372036854775808,72057594037927936,128,1],dtype=np.uint64)
possibleCastles = np.array([1,2,4,8],dtype=np.uint8)

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
            x = 8-int(fen[3])
            y = ord(fen[3]) - 97
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
                catches = np.bitwise_or.reduce(possibleCatches & (enemy | self.en_passant))
                shadowPieces = np.bitwise_or.reduce(possibleMoves & self.all)
                newMoves = ((possibleMoves & ~shadowPieces & ~(shadowPieces>>np.uint64(8))) | catches) & checkFilter
                if np.any(newMoves):
                    newMoves = nonzeroElements(newMoves)
                    if np.any(allPinned & np.uint64(1 << pieceFieldNumber)):
                        king = np.max(color & self.pieceList[5])
                        kingNumber = toNumber(king)
                        if (between[n][kingNumber] & newMoves) or (between[kingNumber][toNumber(newMoves)] & n):
                            for i in newMoves[np.nonzero(newMoves)]:
                                moves.append((n,i,0,(n>>np.uint64(16)==i),np.uint64(0),np.uint64(0)))
                    else:
                        promotions = nonzeroElements(newMoves & whitePromotions)
                        for i in promotions:
                            x = 0
                            while x < 3:
                                moves.append((n,i,0,False,False,np.uint(1<<x)))
                                x += 1
                        newMoves = nonzeroElements(newMoves & ~np.bitwise_or.reduce(promotions))
                        for i in newMoves:
                            moves.append((n,i,0,(n>>np.uint64(16)==i),np.uint64(0),np.uint64(0)))
        else:
            for n in nonzeroElements(self.pieceList[0] & color):
                pieceFieldNumber = toNumber(n)
                possibleMoves = allMoves[0][pieceFieldNumber][1][0]
                possibleCatches = allMoves[0][pieceFieldNumber][1][1]
                catches = np.bitwise_or.reduce(possibleCatches & (enemy | self.en_passant))
                shadowPieces = np.bitwise_or.reduce(possibleMoves & self.all)
                newMoves = ((possibleMoves & ~shadowPieces & ~(shadowPieces<<np.uint64(8))) | catches) & checkFilter
                if np.any(newMoves):
                    newMoves = nonzeroElements(newMoves)
                    if np.any(allPinned & n):
                        king = np.max(color & self.pieceList[5])
                        kingNumber = toNumber(king)
                        if (between[n][kingNumber] & newMoves) or (between[kingNumber][toNumber(newMoves)] & n):
                            for i in newMoves[np.nonzero(newMoves)]:
                                moves.append((n,i,0,(n<<np.uint64(16)==i),np.uint64(0),np.uint64(0)))
                    else:
                        promotions = nonzeroElements(newMoves & whitePromotions)
                        for i in promotions:
                            x = 0
                            while x < 3:
                                moves.append((n,i,0,False,np.uint64(0),np.uint(1<<x)))
                        newMoves = nonzeroElements(newMoves & ~np.bitwise_or.reduce(promotions))
                        for i in newMoves:
                            moves.append((n,i,0,(n<<np.uint64(16)==i),np.uint64(0),np.uint64(0)))
        return moves

    def getRookMoves(self,color,enemy,allPinned,checkFilter):
        moves = []
        for n in nonzeroElements(self.pieceList[1] & color):
            pieceFieldNumber = toNumber(n)
            possibleMoves = allMoves[2][pieceFieldNumber][1]
            colorShadowPieces = nonzeroElements(possibleMoves & color)
            colorShadows = np.bitwise_or.reduce(allShadows[0][pieceFieldNumber][toNumber(colorShadowPieces)])
            newMoves = (possibleMoves & ~(colorShadows | np.bitwise_or.reduce(colorShadowPieces))) & checkFilter
            if np.any(newMoves):
                enemyShadowPieces = nonzeroElements(newMoves & enemy)
                enemyShadows = np.bitwise_or.reduce(allShadows[0][n][toNumber(enemyShadowPieces)])
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
            colorShadows = np.bitwise_or.reduce(allShadows[1][pieceFieldNumber][toNumber(colorShadowPieces)])
            newMoves = (possibleMoves & ~(colorShadows | np.bitwise_or.reduce(colorShadowPieces))) & checkFilter
            if np.any(newMoves):
                enemyShadowPieces = nonzeroElements(newMoves & enemy)
                enemyShadows = np.bitwise_or.reduce(allShadows[1][n][toNumber(enemyShadowPieces)])
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
                    if not attacked(self,enemy,toNumber(i),self.isWhite):
                        moves.append((n,i,5,False,np.uint64(0),np.uint64(0)))
            if self.castle:
                if not attacked(self,enemy,self.isWhite,n):
                    if (self.isWhite and (self.castle & 1)) or (not self.isWhite and (self.castle & 4)):
                        if not (n << np.uint64(1) & self.all) and not (n << np.uint64(2) & self.all) and not attacked(self,enemy,self.isWhite,n << np.uint64(1)) and not attacked(self,enemy,self.isWhite,n << np.uint64(2)):
                            if self.isWhite:
                                moves.append((n,n << np.uint64(2),5,False,np.uint64(1),np.uint64(0)))
                            else:
                                moves.append((n,n << np.uint64(2),5,False,np.uint64(2),np.uint64(0)))
                    if (self.isWhite and (self.castle & 2)) or (not self.isWhite and (self.castle & 8)):
                        if not (n >> np.uint64(1) & self.all) and not (n >> np.uint64(2) & self.all) and not (n >> np.uint64(3) & self.all) and not attacked(self,enemy,self.isWhite,n >> np.uint64(1)) and not attacked(self,enemy,self.isWhite,n >> np.uint64(2)):
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
            colorShadows = np.bitwise_or.reduce(allShadows[0][pieceFieldNumber][toNumber(colorShadowPieces)])
            newMoves = (possibleMoves & ~(colorShadows | np.bitwise_or.reduce(colorShadowPieces))) & checkFilter
            if np.any(newMoves):
                enemyShadowPieces = nonzeroElements(newMoves & enemy)
                enemyShadows = np.bitwise_or.reduce(allShadows[0][n][toNumber(enemyShadowPieces)])
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
            colorShadows = np.bitwise_or.reduce(allShadows[1][pieceFieldNumber][toNumber(colorShadowPieces)])
            newMoves = (possibleMoves & ~(colorShadows | np.bitwise_or.reduce(colorShadowPieces))) & checkFilter
            if np.any(newMoves):
                enemyShadowPieces = nonzeroElements(newMoves & enemy)
                enemyShadows = np.bitwise_or.reduce(allShadows[1][n][toNumber(enemyShadowPieces)])
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
        fromField = move[0]
        toField = move[1]
        piece = move[2]
        en_passant = move[3]
        castle = move[4]
        promotion = move[5]
        ##pieceNr == 0-Pawn, 1-Rook, 2-Knight, 3-Bishop, 4-Queen, 5-King
        self.all = (self.all | toField) & ~fromField
        self.fullmove += 1
        self.halfmove += 1
        self.pieceList[0] = nonzeroElements(self.pieceList[0] & ~toField)
        self.pieceList[1] = nonzeroElements(self.pieceList[1] & ~toField)
        self.pieceList[2] = nonzeroElements(self.pieceList[2] & ~toField)
        self.pieceList[3] = nonzeroElements(self.pieceList[3] & ~toField)
        self.pieceList[4] = nonzeroElements(self.pieceList[4] & ~toField)
        
        if not persistant:
            self.moveHistoryAB.append(move)

        if self.isWhite:
            oldEnPassant = self.en_passant<<np.uint64(8)
        else:
            oldEnPassant = self.en_passant>>np.uint64(8)
        self.en_passant = np.uint64(0)
        if not piece:
            self.halfmove = 0
            self.pieceList[0] = nonzeroElements(self.pieceList[0]& ~fromField)
            if promotion:
                if promotion & 1:
                    self.pieceList[1] = np.append(self.pieceList[1], toField)
                elif promotion & 2:
                    self.pieceList[2] = np.append(self.pieceList[2], toField)
                elif promotion & 4:
                    self.pieceList[3] = np.append(self.pieceList[3], toField)
                elif promotion & 8:
                    self.pieceList[4] = np.append(self.pieceList[4], toField)
            elif en_passant:
                if self.isWhite:
                    self.en_passant = fromField>>np.uint64(8)
                else:
                    self.en_passant = fromField<<np.uint64(8)
                self.pieceList[0] = nonzeroElements(self.pieceList[0] & ~toField)
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
                    self.pieceList[1] = nonzeroElements(np.append(self.pieceList[1], np.uint64(1 << 61)) & ~np.uint64(1 << 63))
                    self.white = (self.white & ~np.uint64(1 << 63)) | np.uint64(1 << 61)
                elif castle & 4:
                    self.pieceList[1] = nonzeroElements(np.append(self.pieceList[1], np.uint64(1 << 5)) & ~np.uint64(1 << 7))
                    self.black = (self.black & ~np.uint64(1 << 7)) | np.uint64(1 << 5)
                elif castle & 2:
                    self.pieceList[1] = nonzeroElements(np.append(self.pieceList[1], np.uint64(1 << 59)) & ~np.uint64(1 << 56))
                    self.white = (self.white & ~np.uint64(1 << 56)) | np.uint64(1 << 59)
                elif castle & 8:
                    self.pieceList[1] = nonzeroElements(np.append(self.pieceList[1], np.uint64(1 << 3)) & ~np.uint64(1))
                    self.black = (self.black & ~np.uint64(1)) | np.uint64(1 << 3)
                self.all = self.black | self.white
        if self.isWhite:
            if not(toField & self.black):
                self.halfmove = 0
            white = self.black & ~toField
            self.black = (self.white | toField) & ~fromField
            self.white = white
        else:
            if not(toField & self.white):
                self.halfmove = 0
            black = self.white & ~toField
            self.white = (self.black | toField) & ~fromField
            self.black = black
        self.isWhite = not self.isWhite
        return self

    def undoMove(self, move):
        pass

    def undoAllMoves(self):
        while len(self.moveHistoryAB) > 0:
            move = self.moveHistoryAB.pop()
            self.undoMove(move)


def getFen(fen):
    self = Board(fen)
    moves = self.getMoves()
    return moves ##toFen(doMove(self,moves[0][0],moves[0][1],moves[0][2],moves[0][3],moves[0][4],moves[0][5]))
