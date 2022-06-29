from typing import Union
import numpy as np
from moves import *
import time
from copy import deepcopy

#gibt die Stringrepresentation eines spezifischen aktivierten Bits zurück Bsp: 1 --> A8
def fieldToString(field: np.uint64):
    field = np.ceil(np.log2(field)).astype(int)
    y = field%8
    x = (field - y) / 8
    txt = 'abcdefgh'[int(y)] + '12345678'[int(7-x)]
    return txt

#gibt für die Nummer den spezifischen Spielsteintyp zurück
def numberToPiece(number):
    if number == 0:
        return 'Pawn'
    if number == 1:
        return 'Rook'
    if number == 2:
        return 'Knight'
    if number == 3:
        return 'Bishop'
    if number == 4:
        return 'Queen'
    if number == 5:
        return 'King'
    return '-'

#gibt die Nummer des Spielfeldes zurück welches dem Exponenten der Bitrepräsentation entspricht Bsp: B8 = 2 = 2^1 = 0x10 --> 1
def toNumber(field: Union[np.ndarray, np.uint64]) -> Union[np.ndarray, np.uint64]:
    field = np.ceil(np.log2(field)).astype(int)
    return field

#gibt die Position aller gesetzten Bits als Builder Objekt zurück über das man iterieren kann Bsp: 3 = 0x11 --> 0 und 1
def bits(n):
    while n:
        b = n & (~n+np.uint(1))
        yield toNumber(b)
        n ^= b

#Gibt ein Tuple zurück wobei der erste Eintrag die attackierten Felder angibt und der Zweit angibt ob es mehrere attackierende Figuren gibt
def attacked(board, enemy: np.ndarray,white: bool,field: np.uint64, all):
    if not np.any(field):
        print(toFen(board))
        return (np.uint64(0), False)
    field = np.max(toNumber(field))
    if (enemy & board.pieceBitboards[2] & allMoves[5][field][2]):
        return ((enemy & board.pieceBitboards[2] & allMoves[5][field][2]), False)
    if (enemy & board.pieceBitboards[5] & allMoves[4][field][2]):
        return ((enemy & board.pieceBitboards[5] & allMoves[4][field][2]), False)
    if white and (enemy & board.pieceBitboards[0] & allMoves[1][field][2][1]):
        return ((enemy & board.pieceBitboards[0] & allMoves[1][field][2][1]), False)
    if not white and (enemy & board.pieceBitboards[0] & allMoves[0][field][2][1]):
        return ((enemy & board.pieceBitboards[0] & allMoves[0][field][2][1]),False)
    attackerPieces = np.append((allMoves[2][field][1] & (board.pieceBitboards[4] | board.pieceBitboards[1]) & enemy), (allMoves[3][field][1] & (board.pieceBitboards[4] | board.pieceBitboards[3]) & enemy))
    if np.any(attackerPieces):
        attackers = np.uint64(0)
        attackersNumber = 0
        for n in nonzeroElements(attackerPieces):
            blockers = between[field][toNumber(n)] & all
            if not blockers:
                attackersNumber += 1
                attackers |= between[field][toNumber(n)] | n
        if attackersNumber == 2:
            return (attackers,True)
        else: 
            return (attackers,False)
    return (np.uint64(0),False)

#gibt zurück auf welche Felder Figuren ziehen können welche den König angreifen. Falls er nicht im Schach steht --> 0
def inCheck(board, color: np.uint64, enemy: np.uint64, white: bool, all):
    kingN = nonzeroElements(board.pieceList[5] & color)
    result = 0
    if attacked(board, enemy, white, kingN, all)[0] > 0:
        result = 1
    return result

#returned den Fen der Boardinstanz
def toFen(board):
    boardTxt = ['-']*64
    for n in board.pieceList[0]:
        boardTxt[toNumber(n)] = 'p'
    for n in board.pieceList[1]:
        boardTxt[toNumber(n)] = 'r'
    for n in board.pieceList[2]:
        boardTxt[toNumber(n)] = 'n'
    for n in board.pieceList[3]:
        boardTxt[toNumber(n)] = 'b'
    for n in board.pieceList[4]:
        boardTxt[toNumber(n)] = 'q'
    for n in board.pieceList[5]:
        boardTxt[toNumber(n)] = 'k'
    for n in bits(board.white):
        boardTxt[n] = boardTxt[n].upper()
    fen = ''
    x = 0
    i = 0
    while x < 8:
        y = 0
        while y < 8:
            if boardTxt[x*8+y] == '-':
                i += 1
            else:
                if i != 0:
                    fen += str(i)
                fen += boardTxt[x*8+y]
                i = 0
            if y == 7 and i != 0:
                fen += str(i)
                i = 0
            y += 1
        if x != 7:
            fen += '/'
        x += 1
    fen += ' '

    if board.isWhite:
        fen += 'w'
    else:
        fen += 'b'
    fen += ' '

    if board.castle:
        if 1 & board.castle:
            fen += 'K'
        if 2 & board.castle:
            fen += 'Q'
        if 4 & board.castle:
            fen += 'k'
        if 8 & board.castle:
            fen += 'q'
    else:
        fen += '-'
    fen += ' '

    if board.en_passant:
        i = np.max(toNumber(board.en_passant))
        y = int((i % 8))
        x = int(8 - ((i - y) / 8))
        fen += chr(y + 97) + str(x)
    else:
        fen += '-'
    fen += ' '

    fen += str(board.halfmove) + ' ' + str(board.fullmove)
    return fen

#gibt alle Elemente eines Numpyarrays zurück die nicht null sind
def nonzeroElements(array: np.ndarray):
    return array[np.nonzero(array)]

#gibt Bitboard aller Pieces zurück die zwischen dem König und einem gegnerischen Bishop Rook oder Queen stehen ohne das eine andere Figure dazwischen steht
def pinned(board, color: np.uint64, enemy: np.uint64):
    king = np.max(board.pieceList[5] & color)
    kNumber = toNumber(king)
    # attackers = np.append((allMoves[2][kNumber][1] & (np.bitwise_or.reduce(board.pieceList[4]) | np.bitwise_or.reduce(board.pieceList[1])) & enemy), (allMoves[3][kNumber][1] & (np.bitwise_or.reduce(board.pieceList[4]) | np.bitwise_or.reduce(board.pieceList[3])) & enemy))
    pinned = np.uint64(0)
    # for n in nonzeroElements(attackers):
    #     blockers = between[kNumber][toNumber(n)] & board.all
    #     if popcount_zero(blockers) == 1:
    #         pinned |= blockers & color
    return pinned

def getFigure(num):
    result = ''
    if num == 2:
        result = 'N'
    elif num == 3:
        result = ''
    elif num == 4:
        result = ''
    elif num == 5:
        result = ''
    return result

def isBeat(isBeatable):
    result = '-'
    if isBeatable:
        result ='x'
    return result

def isGameDone(board):
    if board.isWhite:
        color = board.white
    else:
        color = board.black
    result = isMate(board) or isRemis(board) or isKingOfTheHill(board, color)
    return result

def isMate(board):
    if board.isWhite:
        color = board.white
        enemy = board.black
    else:
        enemy = board.white
        color = board.black
    return (board.moves == [] and inCheck(board, color, enemy, board.isWhite, board.all)[0])

def isRemis(board):
    if board.isWhite:
        color = board.white
        enemy = board.black
    else:
        enemy = board.white
        color = board.black
    # TODO: Other Remis..
    isStaleMate = board.moves == [] and not inCheck(board, color, enemy, board.isWhite, board.all)
    return (board.halfmove == 100 or isStaleMate)

def isKingOfTheHill(board, color):
    """To check if a given color is King of the hill 

    Args:
        `board`: Board to be checked
        `color`: color which could be King of the hill

    Returns:
        1 if color is King of the hill, 0 otherwise
    """
    for n in board.pieceList[5] & color:
        if n == 2**27 or n == 2**28 or n == 2**35 or n == 2**36:
            return True        
    return False


def now():
    return time.time()*1000

def iterativeDeepening(timeLimit, board, alpha, beta, maximizingPlayer, list):
    endTime = now() + timeLimit
    depth = 1
    result = 0
    while True:
        if now() >= endTime:
            break
        result = alphabeta(board, depth, alpha, beta, maximizingPlayer, True, list)
        depth += 1
    return result

def minimax(board, depth, maximizingPlayer):
    if depth == 0 or isGameDone(board):
        value = evalBoard(board)
        return value
    if maximizingPlayer:
        value = float('-inf')
        moves = board.getMoves()
        for child in moves:
            value = max(value, minimax(board.doMove(child), depth-1, False))
            move = board.moveHistoryAB.pop()
            board.undoMove(move)
        return value
    else:
        value = float('inf')
        moves = board.getMoves()
        for child in moves:
            value = min(value, minimax(board.doMove(child), depth-1, True))
            move = board.moveHistoryAB.pop()
            board.undoMove(move)
        return value

def alphaBetaMove(board, depth, alpha, beta):
    result = []
    if depth <= 0:
        return
    moves = board.getMoves()
    for move in moves:
        board.doMove(move)
        value = alphabeta(board, depth-1, alpha, beta, False)
        result.append({
                "move": moveToObject(move),
                "value": value
            })
        board.undoLastMove()
        if value >= beta:
            break
    return result

def alphabeta(board, depth, alpha, beta, isMax):
    # TODO doesn't work properly yet. Weird with depth 5 and above. Better way to save next moves and their values? 
    moves = board.getMoves()
    if (depth == 0) or isGameDone(board):
        return evalBoard(board) * (1.1**depth)
    if isMax:
        value = alpha
        for move in moves:
            board.doMove(move)
            value = max(value, alphabeta(board, depth - 1, value, beta, False))
            board.undoLastMove()
            if value >= beta:
                break
        return value
    else:
        value = beta
        for move in moves:
            board.doMove(move)
            value = min(value, alphabeta(board, depth - 1, alpha, value, True))
            board.undoLastMove()
            if value <= alpha:
                break
        return value

def evalBoard(board):
    """ Evaluates a board state by applying a heuritic.

    Args:
        `board`: Board instance that will be evaluated

    Returns:
        A numeric value for the current board state
    """
    color = board.black
    enemy = board.white
    if board.isWhite:
        color = board.white
        enemy = board.black
    pawnDelta = nonzeroElements(
        board.pieceList[0] & color).size - nonzeroElements(board.pieceList[0] & enemy).size
    rookDelta = nonzeroElements(
        board.pieceList[1] & color).size - nonzeroElements(board.pieceList[1] & enemy).size
    knightDelta = nonzeroElements(
        board.pieceList[2] & color).size - nonzeroElements(board.pieceList[2] & enemy).size
    bishopDelta = nonzeroElements(
        board.pieceList[3] & color).size - nonzeroElements(board.pieceList[3] & enemy).size
    queenDelta = nonzeroElements(
        board.pieceList[4] & color).size - nonzeroElements(board.pieceList[4] & enemy).size
    check = inCheck(board, enemy, color, not board.isWhite, board.all) - inCheck(board, color, enemy, board.isWhite, board.all)
    result = 10 * check + 9 * queenDelta + 5 * rookDelta + 3 * knightDelta + 3 * bishopDelta + 1 * pawnDelta
    
    kingOfTheHill = isKingOfTheHill(board, color) - isKingOfTheHill(board, enemy)
    
    if kingOfTheHill != 0: 
        result = kingOfTheHill
    
    if isRemis(board):
        result = -1
    # if isKingOfTheHill(board) or isMate(board):
    #     result = factor * 10000
    return result


def moveToObject(move):
    object = {}
    object['fromField'] = fieldToString(move[0])
    object['toField'] = fieldToString(move[1])
    object['figure'] = getFigure(move[2])
    object['enPassant'] = bool(move[3])
    object['castle'] = bool(move[4])
    object['promotion'] = bool(move[5])
    return object

def movesToJSON(moves):
    list = []
    for move in moves:
        list.append(moveToObject(move))
    return {'moves': list}

def movesToJSON2(moves):
    list = []
    for node in moves:
        move = node[0]
        value = node[1]
        childVal = node[2]
        object = {}
        object['fromField'] = fieldToString(move[0])
        object['toField'] = fieldToString(move[1])
        object['figure'] = getFigure(move[2])
        object['enPassant'] = bool(move[3])
        object['castle'] = bool(move[4])
        object['promotion'] = bool(move[5])
        object['value'] = value
        object['valOfChild'] = childVal

        list.append(object)
    return {'moves': list}

def popcount_zero(x):
    c = 0
    while x:
        x &= x - np.uint(1)
        c += 1
    return c