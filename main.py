from moves import *
import numpy as np
from utils import *

whitePromotions = np.uint64(18374686479671623680)
blackPromotions = np.uint64(255)

max = 'w'

class Board:
    def __init__(self, all: np.uint64, pawn: np.array, rook: np.array, knight: np.array, bishop: np.array, queen: np.array,
                 king: np.array, black: np.uint64, white: np.uint64, castle: np.uint8, en_passant: np.uint64, halfmove: int, fullmove: int, player=True):
        self.all = all
        self.pawn = pawn
        self.rook = rook
        self.knight = knight
        self.bishop = bishop
        self.queen = queen
        self.king = king
        self.white = white
        self.black = black
        self.castle = castle
        self.en_passant = en_passant
        self.halfmove = halfmove
        self.fullmove = fullmove
        self.player = player
        
def setMax(newMax):
    max = newMax

def getFen(fen):
    info = fen.split()
    board = getBoard(info)
    if info[1] == 'w':
        white = True
        color = board.white
        enemy = board.black
    else:
        white = False
        board.player = False
        color = board.black
        enemy = board.white
    print(board.rook)
    moves = getMoves(board,color,enemy,white)
    print(len(moves))
    print(moves)
    return moves ##toFen(doMove(board,moves[0][0],moves[0][1],moves[0][2],moves[0][3],moves[0][4],moves[0][5]))

def getBoard(fen):
    fenArray = fen[0].split('/')
    all = np.uint64(0)
    pawn = np.array([],dtype=np.uint64)
    rook = np.array([],dtype=np.uint64)
    knight = np.array([],dtype=np.uint64)
    bishop = np.array([],dtype=np.uint64)
    queen = np.array([],dtype=np.uint64)
    king = np.uint64(0)
    white = np.uint64(0)
    black = np.uint64(0)
    x = 0
    for i in fenArray:
        for j in i:
            if j >= '0' and j <= '9':
                x += int(j)
            else:
                z = 1 << x
                all |= np.uint64(z)
                if j.isupper():
                    white |= np.uint64(z)
                else:
                    black |= np.uint64(z)
                if j == 'p' or j == 'P':
                    pawn = np.append(pawn, np.uint64(z))
                elif j == 'r' or j == 'R':
                    rook = np.append(rook, np.uint64(z))
                elif j == 'n' or j == 'N':
                    knight = np.append(knight, np.uint64(z))
                elif j == 'b' or j == 'B':
                    bishop = np.append(bishop, np.uint64(z))
                elif j == 'q' or j == 'Q':
                    queen = np.append(queen, np.uint64(z))
                elif j == 'k' or j == 'K':
                    king = np.append(king, np.uint64(z))
                x += 1

    castle = np.uint8(0)
    for i in fen[2]:
        if i == 'K':
            castle |= np.uint8(1)
        if i == 'Q':
            castle |= np.uint8(2)
        if i == 'k':
            castle |= np.uint8(4)
        if i == 'q':
            castle |= np.uint8(8)

    en_passant = np.uint64(0)
    if fen[3] != '-':
        x = 8-int(fen[3])
        y = ord(fen[3]) - 97
        en_passant |= np.uint64(1 << (x*8+y))
    

    board = Board(all,pawn,rook,knight,bishop,queen,king,black,white,castle, en_passant, int(fen[4]), int(fen[5]))
    return board

def getMoves(board,color,enemy,white):
    moves = []
    allPinned = np.uint64(0)
    ##allPinned = pinned(board,color,enemy)
    checkFilter = np.uint64((1<<64)-1)
    ##attacker = inCheck(board,color,enemy,white)
    ##if inCheck(board,color,enemy,white):
        ##checkFilter = between[toNumber(attacker) - 1][(board.king & color).bit_length() - 1] | attacker | (board.king & color)
    moves.extend(getRookMoves(board,color,enemy,allPinned,checkFilter))
    ##moves.extend(getBishopMoves(board,color,enemy,allPinned,checkFilter))
    moves.extend(getPawnMoves(board,color,enemy,allPinned,white,checkFilter))
    ##moves.extend(getKnightMoves(board,color,allPinned,checkFilter))
    ##moves.extend(getKingMoves(board,color,enemy,white))
    ##moves.extend(getQueenMoves(board,color,enemy,allPinned,checkFilter))
    return moves

def getPawnMoves(board,color,enemy,allPinned,white,checkFilter):
    moves = []
    if white:
        for n in nonzeroElements(board.pawn & color):
            pieceFieldNumber = toNumber(n)
            possibleMoves = allMoves[1][pieceFieldNumber][1][0]
            possibleCatches = allMoves[1][pieceFieldNumber][1][1]
            catches = np.bitwise_or.reduce(possibleCatches & (enemy | board.en_passant))
            shadowPieces = np.bitwise_or.reduce(possibleMoves & board.all)
            newMoves = ((possibleMoves & ~shadowPieces & ~(shadowPieces>>np.uint64(8))) | catches) & checkFilter
            if np.any(newMoves):
                newMoves = nonzeroElements(newMoves)
                if np.any(allPinned & np.uint64(1 << pieceFieldNumber)):
                    king = np.max(color & board.king)
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
        for n in nonzeroElements(board.pawn & color):
            pieceFieldNumber = toNumber(n)
            possibleMoves = allMoves[0][pieceFieldNumber][1][0]
            possibleCatches = allMoves[0][pieceFieldNumber][1][1]
            catches = np.bitwise_or.reduce(possibleCatches & (enemy | board.en_passant))
            shadowPieces = np.bitwise_or.reduce(possibleMoves & board.all)
            newMoves = ((possibleMoves & ~shadowPieces & ~(shadowPieces<<np.uint64(8))) | catches) & checkFilter
            if np.any(newMoves):
                newMoves = nonzeroElements(newMoves)
                if np.any(allPinned & n):
                    king = np.max(color & board.king)
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

def getRookMoves(board,color,enemy,allPinned,checkFilter):
    moves = []
    for n in nonzeroElements(board.rook & color):
        pieceFieldNumber = toNumber(n)
        possibleMovesArray = allMoves[2][pieceFieldNumber][1]
        possibleMovesBit = allMoves[2][pieceFieldNumber][2]
        colorShadowPieces = possibleMovesArray & color
        colorShadowPieces = colorShadowPieces[np.nonzero(colorShadowPieces)]
        colorShadows = np.bitwise_or.reduce(allShadows[0][pieceFieldNumber][toNumber(colorShadowPieces)])
        newMoves = (possibleMovesArray & ~(colorShadows | np.bitwise_or.reduce(colorShadowPieces))) & checkFilter
        if np.any(newMoves):
            enemyShadowPieces = nonzeroElements(newMoves & enemy)
            enemyShadows = np.bitwise_or.reduce(allShadows[0][n][toNumber(enemyShadowPieces)])
            newMoves &= ~enemyShadows
            newMoves = nonzeroElements(newMoves)
            if allPinned & n:
                    king = np.max(color & board.king)
                    kingNumber = toNumber(king)
                    place = n
                    for i in newMoves:
                        if (between[pieceFieldNumber][kingNumber] & i) or (between[kingNumber][toNumber(i)] & place):
                            moves.append((n,i,1,False,0,0))
            else:
                for i in newMoves:
                    moves.append((n,i,1,False,0,0))
    return moves

def getBishopMoves(board,color,enemy,allPinned,checkFilter):
    moves = []
    for n in bits(board.bishop & color):
        possibleMoves = allMoves[3][n]
        whiteShadowPieces = possibleMoves[1] & color
        whiteShadows = 0
        for i in bits(whiteShadowPieces):
            whiteShadows |= allShadows[1][n][1][i]
        newMoves = (possibleMoves[1] & ~(whiteShadows | whiteShadowPieces)) & checkFilter
        if newMoves:
            blackShadowPieces = newMoves & enemy
            blackShadows = 0
            for i in bits(blackShadowPieces):
                blackShadows |= allShadows[1][n][1][i]
            newMoves &= ~blackShadows
            if allPinned & 1 << n:
                    king = color & board.king
                    kingNumber = king.bit_length() - 1
                    place = 1 << n
                    for i in bits(newMoves):
                        if (between[n][kingNumber] & 1 << i) or (between[kingNumber][i] & place):
                            moves.append((possibleMoves[0],1 << i,4,False,0,0))
            else:
                for i in bits(newMoves):
                    moves.append((possibleMoves[0],1 << i,4,False,0,0))
    return moves

def getKnightMoves(board,color,allPinned,checkFilter):
    moves = []
    for n in bits(board.knight & color):
        possibleMoves = allMoves[5][n]
        shadowPieces = possibleMoves[1] & color
        newMoves = (possibleMoves[1] & ~shadowPieces) & checkFilter
        if newMoves:
            if allPinned & 1 << n:
                    king = color & board.king
                    kingNumber = king.bit_length() - 1
                    place = 1 << n
                    for i in bits(newMoves):
                        if (between[n][kingNumber] & 1 << i) or (between[kingNumber][i] & place):
                            moves.append((possibleMoves[0],1 << i,2,False,0,0))
            else:
                for i in bits(newMoves):
                    moves.append((possibleMoves[0],1 << i,2,False,0,0))
    return moves

def getKingMoves(board,color,enemy,white):
    moves = []
    for n in bits(board.king & color):
        possibleMoves = allMoves[4][n]
        shadowPieces = possibleMoves[1] & color
        newMoves = possibleMoves[1] & ~shadowPieces
        if newMoves:
            for i in bits(newMoves):
                if not attacked(board,enemy,white,i):
                    moves.append((possibleMoves[0],1 << i,16,False,0,0))
        if board.castle:
            if not attacked(board,enemy,white,n):
                kingF = 1 << n
                if (white and (board.castle & 1)) or (not white and (board.castle & 4)):
                    if not (kingF << 1 & board.all) and not (kingF << 2 & board.all) and not attacked(board,enemy,white,n+1) and not attacked(board,enemy,white,n+2):
                        if white:
                            moves.append((kingF,kingF<<2,16,False,1,0))
                        else:
                            moves.append((kingF,kingF<<2,16,False,2,0))
                if (white and (board.castle & 2)) or (not white and (board.castle & 8)):
                    if not (kingF >> 1 & board.all) and not (kingF >> 2 & board.all) and not (kingF >> 3 & board.all) and not attacked(board,enemy,white,n+1) and not attacked(board,enemy,white,n+2):
                        if white:
                            moves.append((kingF,kingF>>2,16,False,4,0))
                        else:
                            moves.append((kingF,kingF>>2,16,False,8,0))
    return moves

def getQueenMoves(board,color,enemy,allPinned,checkFilter):
    moves = []
    for n in bits(board.queen & color):
        possibleMoves = allMoves[2][n]
        whiteShadowPieces = possibleMoves[1] & color
        whiteShadows = 0
        for i in bits(whiteShadowPieces):
            whiteShadows |= allShadows[0][n][1][i]
        newMoves = (possibleMoves[1] & ~(whiteShadows | whiteShadowPieces)) & checkFilter
        if newMoves:
            blackShadowPieces = newMoves & enemy
            blackShadows = 0
            for i in bits(blackShadowPieces):
                blackShadows |= allShadows[0][n][1][i]
            newMoves &= ~blackShadows
            if allPinned & 1 << n:
                    king = color & board.king
                    kingNumber = king.bit_length() - 1
                    place = 1 << n
                    for i in bits(newMoves):
                        if (between[n][kingNumber] & 1 << i) or (between[kingNumber][i] & place):
                            moves.append((possibleMoves[0],1 << i,8,False,0,0))
            else:
                for i in bits(newMoves):
                    moves.append((possibleMoves[0],1 << i,8,False,0,0))
    for n in bits(board.queen & color):
        possibleMoves = allMoves[3][n]
        whiteShadowPieces = possibleMoves[1] & color
        whiteShadows = 0
        for i in bits(whiteShadowPieces):
            whiteShadows |= allShadows[1][n][1][i]
        newMoves = (possibleMoves[1] & ~(whiteShadows | whiteShadowPieces)) & checkFilter
        if newMoves:
            blackShadowPieces = newMoves & enemy
            blackShadows = 0
            for i in bits(blackShadowPieces):
                blackShadows |= allShadows[1][n][1][i]
            newMoves &= ~blackShadows
            if allPinned & 1 << n:
                    king = color & board.king
                    kingNumber = king.bit_length() - 1
                    place = 1 << n
                    for i in bits(newMoves):
                        if (between[n][kingNumber] & 1 << i) or (between[kingNumber][i] & place):
                            moves.append((possibleMoves[0],1 << i,8,False,0,0))
            else:
                for i in bits(newMoves):
                    moves.append((possibleMoves[0],1 << i,8,False,0,0))
    return moves
    
def pinned(board, color, enemy):
    king = board.king & color
    kNumber = king.bit_length() - 1
    attackers = (allMoves[2][kNumber][1] & (board.queen | board.rook) & enemy) | (allMoves[3][kNumber][1] & (board.queen | board.bishop) & enemy) 
    pinned = 0
    for n in bits(attackers):
        blockers = between[kNumber][n] & board.all
        if blockers.bit_count() == 1:
            pinned |= blockers & color
    return pinned

def attacked(board,enemy,white,field):
    if enemy & board.knight & allMoves[5][field][1]:
        return enemy & board.knight & allMoves[5][field][1]
    if enemy & board.king & allMoves[4][field][1]:
        return enemy & board.king & allMoves[4][field][1]
    if white and (enemy & board.pawn & allMoves[0][field][1][1]):
        return enemy & board.pawn & allMoves[0][field][1][1]
    if not white and (enemy & board.pawn & allMoves[1][field][1][1]):
        return enemy & board.pawn & allMoves[1][field][1][1]
    attackers = (allMoves[2][field][1] & (board.queen | board.rook) & enemy) | (allMoves[3][field][1] & (board.queen | board.bishop) & enemy) 
    for i in bits(attackers):
        blockers = between[field][i] & board.all
        if not blockers:
            return 1 << i
    return 0
    
def inCheck(board,color,enemy,white):
    kingN = board.king & color
    return attacked(board,enemy,white,kingN.bit_length() - 1)

def doMove(board,fromField,toField,piece,en_passant,castle,promotion):
    all = (board.all | toField) & ~fromField
    en_passantNew = 0
    castleNew = board.castle
    white = board.player
    halfmove = board.halfmove + 1
    if white:
        blackPieces = board.black & ~toField
        whitePieces = (board.white | toField) ^ fromField
        if (blackPieces & ~board.black):
            halfmove = 0
    else:
        whitePieces = board.white & ~toField
        blackPieces = (board.black | toField) ^ fromField
        if (whitePieces & ~board.white):
            halfmove = 0
    if not piece:
        halfmove = 0
        rook = board.rook & ~toField
        knight = board.knight & ~toField
        bishop = board.bishop & ~toField
        queen = board.queen & ~toField
        king = board.king & ~toField
        if promotion:
            if promotion & 1:
                rook = board.rook | toField
                pawn = board.pawn ^ fromField
            elif promotion & 2:
                knight = board.knight | toField
                pawn = board.pawn ^ fromField
            elif promotion & 4:
                bishop = board.bishop | toField
                pawn = board.pawn ^ fromField
            elif promotion & 8:
                queen = board.queen | toField
                pawn = board.pawn ^ fromField
        elif en_passant:
            if board.player:
                en_passantNew = fromField>>8
            else:
                en_passantNew = fromField<<8
            pawn = (board.pawn | toField) ^ fromField
        else:
            pawn = (board.pawn | toField) ^ fromField
    elif piece & 1:
        rook = (board.rook | toField) ^ fromField
        pawn = board.pawn & ~toField
        knight = board.knight & ~toField
        bishop = board.bishop & ~toField
        queen = board.queen & ~toField
        king = board.king & ~toField
    elif piece & 2:
        knight = (board.knight | toField) ^ fromField
        pawn = board.pawn & ~toField
        rook = board.rook & ~toField
        bishop = board.bishop & ~toField
        queen = board.queen & ~toField
        king = board.king & ~toField
    elif piece & 4:
        bishop = (board.bishop | toField) ^ fromField
        pawn = board.pawn & ~toField
        rook = board.rook & ~toField
        knight = board.knight & ~toField
        queen = board.queen & ~toField
        king = board.king & ~toField
    elif piece & 8:
        queen = (board.queen | toField) ^ fromField
        pawn = board.pawn & ~toField
        rook = board.rook & ~toField
        knight = board.knight & ~toField
        bishop = board.bishop & ~toField
        king = board.king & ~toField
    elif piece & 16:
        pawn = board.pawn & ~toField
        rook = board.rook & ~toField
        knight = board.knight & ~toField
        bishop = board.bishop & ~toField
        queen = board.queen & ~toField
        if castle:
            if castle & 1:
                king = (board.king | toField) ^ fromField
                rook = (board.rook | (1 << 61)) & ~(1 << 63)
                whitePieces = whitePieces & ~(1 << 63) | rook
            elif castle & 4:
                king = (board.king | toField) ^ fromField
                rook = (board.rook | (1 << 5)) & ~(1 << 7)
                blackPieces = blackPieces & ~(1 << 7) | rook
            elif castle & 2:
                king = (board.king | toField) ^ fromField
                rook = (board.rook | (1 << 59)) & ~(1 << 56)
                whitePieces = whitePieces & ~(1 << 56) | rook
            elif castle & 8:
                king = (board.king | toField) ^ fromField
                rook = (board.rook | (1 << 3)) & ~(1 << 0)
                blackPieces = blackPieces & ~(1 << 0) | rook
            all = (all & ~(board.rook)) | rook
        else:
            king = (board.king | toField) & ~fromField
    return Board(all,pawn,rook,knight,bishop,queen,king,blackPieces,whitePieces,castleNew,en_passantNew,halfmove,board.fullmove + 1,not white)