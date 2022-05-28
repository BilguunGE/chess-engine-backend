from moves import *
import numpy as np
from utils import *

whitePromotions = np.uint64(18374686479671623680)
blackPromotions = np.uint64(255)

max = 'w'

class Board:
    all = np.uint64(0)
    pawn = np.array([], dtype=np.uint64)
    rook = np.array([], dtype=np.uint64)
    knight = np.array([], dtype=np.uint64)
    bishop = np.array([], dtype=np.uint64)
    queen = np.array([], dtype=np.uint64)
    king = np.uint64(0)
    white = np.uint64(0)
    black = np.uint64(0)
    castle = np.uint8(0)
    en_passant = np.uint64(0)
    halfmove = 0
    fullmove = 1
    isWhite = True

    def __init__(self,fenString):
        fen =fenString.split()
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
                        self.pawn = np.append(self.pawn, np.uint64(z))
                    elif j == 'r' or j == 'R':
                        self.rook = np.append(self.rook, np.uint64(z))
                    elif j == 'n' or j == 'N':
                        self.knight = np.append(self.knight, np.uint64(z))
                    elif j == 'b' or j == 'B':
                        self.bishop = np.append(self.bishop, np.uint64(z))
                    elif j == 'q' or j == 'Q':
                        self.queen = np.append(self.queen, np.uint64(z))
                    elif j == 'k' or j == 'K':
                        self.king = np.append(self.king, np.uint64(z))
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
        ##allPinned = pinned(color,enemy)
        checkFilter = np.uint64((1<<64)-1)
        ##attacker = inCheck(color,enemy,white)
        ##if inCheck(self,color,enemy,white):
            ##checkFilter = between[toNumber(attacker) - 1][(self.king & color).bit_length() - 1] | attacker | (self.king & color)
        moves.extend(self.getRookMoves(color,enemy,allPinned,checkFilter))
        moves.extend(self.getBishopMoves(color,enemy,allPinned,checkFilter))
        moves.extend(self.getPawnMoves(color,enemy,allPinned,checkFilter))
        moves.extend(self.getKnightMoves(color,allPinned,checkFilter))
        ##moves.extend(getKingMoves(color,enemy,white))
        ##moves.extend(getQueenMoves(color,enemy,allPinned,checkFilter))
        return moves
       
    def getPawnMoves(self,color,enemy,allPinned,checkFilter):
        moves = []
        if self.isWhite:
            for n in nonzeroElements(self.pawn & color):
                pieceFieldNumber = toNumber(n)
                possibleMoves = allMoves[1][pieceFieldNumber][1][0]
                possibleCatches = allMoves[1][pieceFieldNumber][1][1]
                catches = np.bitwise_or.reduce(possibleCatches & (enemy | self.en_passant))
                shadowPieces = np.bitwise_or.reduce(possibleMoves & self.all)
                newMoves = ((possibleMoves & ~shadowPieces & ~(shadowPieces>>np.uint64(8))) | catches) & checkFilter
                if np.any(newMoves):
                    newMoves = nonzeroElements(newMoves)
                    if np.any(allPinned & np.uint64(1 << pieceFieldNumber)):
                        king = np.max(color & self.king)
                        kingNumber = toNumber(king)
                        if (between[n][kingNumber] & newMoves) or (between[kingNumber][toNumber(newMoves)] & n):
                            for i in newMoves[np.nonzero(newMoves)]:
                                moves.append((n,i,np.uint64(0),(n>>np.uint64(16)==i),np.uint64(0),np.uint64(0)))
                    else:
                        promotions = nonzeroElements(newMoves & whitePromotions)
                        for i in promotions:
                            x = 0
                            while x < 3:
                                moves.append((n,i,np.uint64(0),False,False,np.uint(1<<x)))
                                x += 1
                        newMoves = nonzeroElements(newMoves & ~np.bitwise_or.reduce(promotions))
                        for i in newMoves:
                            moves.append((n,i,np.uint64(0),(n<<np.uint64(16)==i),np.uint64(0),np.uint64(0)))
        else:
            for n in nonzeroElements(self.pawn & color):
                pieceFieldNumber = toNumber(n)
                possibleMoves = allMoves[0][pieceFieldNumber][1][0]
                possibleCatches = allMoves[0][pieceFieldNumber][1][1]
                catches = np.bitwise_or.reduce(possibleCatches & (enemy | self.en_passant))
                shadowPieces = np.bitwise_or.reduce(possibleMoves & self.all)
                newMoves = ((possibleMoves & ~shadowPieces & ~(shadowPieces<<np.uint64(8))) | catches) & checkFilter
                if np.any(newMoves):
                    newMoves = nonzeroElements(newMoves)
                    if np.any(allPinned & n):
                        king = np.max(color & self.king)
                        kingNumber = toNumber(king)
                        if (between[n][kingNumber] & newMoves) or (between[kingNumber][toNumber(newMoves)] & n):
                            for i in newMoves[np.nonzero(newMoves)]:
                                moves.append((n,i,np.uint64(0),(n<<np.uint64(16)==i),np.uint64(0),np.uint64(0)))
                    else:
                        promotions = nonzeroElements(newMoves & whitePromotions)
                        for i in promotions:
                            x = 0
                            while x < 3:
                                moves.append((n,i,np.uint64(0),False,np.uint64(0),np.uint(1<<x)))
                        newMoves = nonzeroElements(newMoves & ~np.bitwise_or.reduce(promotions))
                        for i in newMoves:
                            moves.append((n,i,np.uint64(0),(n<<np.uint64(16)==i),np.uint64(0),np.uint64(0)))
        return moves

    def getRookMoves(self,color,enemy,allPinned,checkFilter):
        moves = []
        for n in nonzeroElements(self.rook & color):
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
                        king = nonzeroElements(color & self.king)
                        kingNumber = toNumber(king)
                        for i in newMoves:
                            if (between[pieceFieldNumber][kingNumber] & i) or (between[kingNumber][toNumber(i)] & n):
                                moves.append((n,i,np.uint64(1),False,np.uint64(0),np.uint64(0)))
                else:
                    for i in newMoves:
                        moves.append((n,i,np.uint64(1),False,np.uint64(0),np.uint64(0)))
        return moves

    def getBishopMoves(self,color,enemy,allPinned,checkFilter):
        moves = []
        for n in nonzeroElements(self.bishop & color):
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
                        king = nonzeroElements(color & self.king)
                        kingNumber = toNumber(king)
                        for i in newMoves:
                            if (between[pieceFieldNumber][kingNumber] & i) or (between[kingNumber][toNumber(i)] & n):
                                moves.append((n,i,np.uint64(4),False,np.uint64(0),np.uint64(0)))
                else:
                    for i in newMoves:
                        moves.append((n,i,np.uint64(4),False,np.uint64(0),np.uint64(0)))
        return moves
    def getKnightMoves(self,color,allPinned,checkFilter):
        moves = []
        for n in nonzeroElements(self.knight & color):
            pieceFieldNumber = toNumber(n)
            possibleMoves = allMoves[5][pieceFieldNumber][1]
            shadowPieces = np.bitwise_or.reduce(possibleMoves & color)
            newMoves = (possibleMoves & ~shadowPieces) & checkFilter
            if np.any(newMoves):
                newMoves = nonzeroElements(newMoves)
                if allPinned & n:
                        king = nonzeroElements(color & self.king)
                        kingNumber = toNumber(king)
                        for i in newMoves:
                            if (between[pieceFieldNumber][kingNumber] & i) or (between[kingNumber][toNumber(i)] & n):
                                moves.append((n,i,np.uint64(2),False,np.uint64(0),np.uint64(0)))
                else:
                    for i in newMoves:
                        moves.append((n,i,np.uint64(2),False,np.uint64(0),np.uint64(0)))
        return moves
    
    def getKingMoves(self,color,enemy):
        moves = []
        for n in bits(self.king & color):
            possibleMoves = allMoves[4][n]
            shadowPieces = possibleMoves[1] & color
            newMoves = possibleMoves[1] & ~shadowPieces
            if newMoves:
                for i in bits(newMoves):
                    if not attacked(self,enemy,self.isWhite,i):
                        moves.append((possibleMoves[0],1 << i,16,False,0,0))
            if self.castle:
                if not attacked(self,enemy,self.isWhite,n):
                    kingF = 1 << n
                    if (self.isWhite and (self.castle & 1)) or (not self.isWhite and (self.castle & 4)):
                        if not (kingF << 1 & self.all) and not (kingF << 2 & self.all) and not attacked(self,enemy,self.isWhite,n+1) and not attacked(self,enemy,self.isWhite,n+2):
                            if self.isWhite:
                                moves.append((kingF,kingF<<2,16,False,1,0))
                            else:
                                moves.append((kingF,kingF<<2,16,False,2,0))
                    if (self.isWhite and (self.castle & 2)) or (not self.isWhite and (self.castle & 8)):
                        if not (kingF >> 1 & self.all) and not (kingF >> 2 & self.all) and not (kingF >> 3 & self.all) and not attacked(self,enemy,self.isWhite,n+1) and not attacked(self,enemy,self.isWhite,n+2):
                            if self.isWhite:
                                moves.append((kingF,kingF>>2,16,False,4,0))
                            else:
                                moves.append((kingF,kingF>>2,16,False,8,0))
        return moves
    
    def getQueenMoves(self,color,enemy,allPinned,checkFilter):
        moves = []
        for n in nonzeroElements(self.queen & color):
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
                        king = nonzeroElements(color & self.king)
                        kingNumber = toNumber(king)
                        for i in newMoves:
                            if (between[pieceFieldNumber][kingNumber] & i) or (between[kingNumber][toNumber(i)] & n):
                                moves.append((n,i,np.uint64(1),False,np.uint64(0),np.uint64(0)))
                else:
                    for i in newMoves:
                        moves.append((n,i,np.uint64(8),False,np.uint64(0),np.uint64(0)))
        for n in nonzeroElements(self.queen & color):
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
                        king = nonzeroElements(color & self.king)
                        kingNumber = toNumber(king)
                        for i in newMoves:
                            if (between[pieceFieldNumber][kingNumber] & i) or (between[kingNumber][toNumber(i)] & n):
                                moves.append((n,i,np.uint64(4),False,np.uint64(0),np.uint64(0)))
                else:
                    for i in newMoves:
                        moves.append((n,i,np.uint64(8),False,np.uint64(0),np.uint64(0)))
        return moves
    
    def doMove(self,fromField,toField,piece,en_passant,castle,promotion):
        all = (self.all | toField) & ~fromField
        en_passantNew = 0
        castleNew = self.castle
        halfmove = self.halfmove + 1
        if self.isWhite:
            blackPieces = self.black & ~toField
            whitePieces = (self.white | toField) ^ fromField
            if (blackPieces & ~self.black):
                halfmove = 0
        else:
            whitePieces = self.white & ~toField
            blackPieces = (self.black | toField) ^ fromField
            if (whitePieces & ~self.white):
                halfmove = 0
        if not piece:
            halfmove = 0
            rook = self.rook & ~toField
            knight = self.knight & ~toField
            bishop = self.bishop & ~toField
            queen = self.queen & ~toField
            king = self.king & ~toField
            if promotion:
                if promotion & 1:
                    rook = self.rook | toField
                    pawn = self.pawn ^ fromField
                elif promotion & 2:
                    knight = self.knight | toField
                    pawn = self.pawn ^ fromField
                elif promotion & 4:
                    bishop = self.bishop | toField
                    pawn = self.pawn ^ fromField
                elif promotion & 8:
                    queen = self.queen | toField
                    pawn = self.pawn ^ fromField
            elif en_passant:
                if self.isWhite:
                    en_passantNew = fromField>>8
                else:
                    en_passantNew = fromField<<8
                pawn = (self.pawn | toField) ^ fromField
            else:
                pawn = (self.pawn | toField) ^ fromField
        elif piece & 1:
            rook = (self.rook | toField) ^ fromField
            pawn = self.pawn & ~toField
            knight = self.knight & ~toField
            bishop = self.bishop & ~toField
            queen = self.queen & ~toField
            king = self.king & ~toField
        elif piece & 2:
            knight = (self.knight | toField) ^ fromField
            pawn = self.pawn & ~toField
            rook = self.rook & ~toField
            bishop = self.bishop & ~toField
            queen = self.queen & ~toField
            king = self.king & ~toField
        elif piece & 4:
            bishop = (self.bishop | toField) ^ fromField
            pawn = self.pawn & ~toField
            rook = self.rook & ~toField
            knight = self.knight & ~toField
            queen = self.queen & ~toField
            king = self.king & ~toField
        elif piece & 8:
            queen = (self.queen | toField) ^ fromField
            pawn = self.pawn & ~toField
            rook = self.rook & ~toField
            knight = self.knight & ~toField
            bishop = self.bishop & ~toField
            king = self.king & ~toField
        elif piece & 16:
            pawn = self.pawn & ~toField
            rook = self.rook & ~toField
            knight = self.knight & ~toField
            bishop = self.bishop & ~toField
            queen = self.queen & ~toField
            if castle:
                if castle & 1:
                    king = (self.king | toField) ^ fromField
                    rook = (self.rook | (1 << 61)) & ~(1 << 63)
                    whitePieces = whitePieces & ~(1 << 63) | rook
                elif castle & 4:
                    king = (self.king | toField) ^ fromField
                    rook = (self.rook | (1 << 5)) & ~(1 << 7)
                    blackPieces = blackPieces & ~(1 << 7) | rook
                elif castle & 2:
                    king = (self.king | toField) ^ fromField
                    rook = (self.rook | (1 << 59)) & ~(1 << 56)
                    whitePieces = whitePieces & ~(1 << 56) | rook
                elif castle & 8:
                    king = (self.king | toField) ^ fromField
                    rook = (self.rook | (1 << 3)) & ~(1 << 0)
                    blackPieces = blackPieces & ~(1 << 0) | rook
                all = (all & ~(self.rook)) | rook
            else:
                king = (self.king | toField) & ~fromField
        self.all = all
        self.pawn =pawn
        self.rook = rook
        self.knight =knight
        self.bishop =bishop
        self.queen = queen
        self.king = king
        self.black =blackPieces
        self.white =whitePieces
        self.castle =castleNew
        self.en_passant =en_passantNew
        self.halfmove = halfmove
        self.fullmove +=1
        self.isWhite = not self.isWhite

def getFen(fen):
    info = fen.split()
    self = getBoard(info)
    if info[1] == 'w':
        white = True
        color = self.white
        enemy = self.black
    else:
        white = False
        self.isWhite = False
        color = self.black
        enemy = self.white
    moves = getMoves(self,color,enemy,white)
    print(len(moves))
    print(moves)
    return moves ##toFen(doMove(self,moves[0][0],moves[0][1],moves[0][2],moves[0][3],moves[0][4],moves[0][5]))
