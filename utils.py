from typing import Union
import numpy as np
from moves import *
import time
from copy import deepcopy


def fieldToString(field: np.uint64):
    field = np.ceil(np.log2(field)).astype(int)
    y = field%8
    x = (field - y) / 8
    txt = 'abcdefgh'[int(y)] + '12345678'[int(7-x)]
    return txt

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

def toNumber(field: Union[np.ndarray, np.uint64]) -> Union[np.ndarray, np.uint64]:
    field = np.ceil(np.log2(field)).astype(int)
    return field

def bits(n):
    while n:
        b = n & (~n+np.uint(1))
        yield toNumber(b)
        n ^= b

def attacked(board, enemy: np.ndarray,white: bool,field: np.uint64, all):
    if not np.any(field):
        return np.uint64(0)
    field = np.max(toNumber(field))
    if (enemy & board.pieceBitboards[2] & allMoves[5][field][2]):
        return (enemy & board.pieceBitboards[2] & allMoves[5][field][2])
    if (enemy & board.pieceBitboards[5] & allMoves[4][field][2]):
        return (enemy & board.pieceBitboards[5] & allMoves[4][field][2])
    if white and (enemy & board.pieceBitboards[0] & allMoves[1][field][2][1]):
        return (enemy & board.pieceBitboards[0] & allMoves[1][field][2][1])
    if not white and (enemy & board.pieceBitboards[0] & allMoves[0][field][2][1]):
        return (enemy & board.pieceBitboards[0] & allMoves[0][field][2][1])
    attackerPieces = np.append((allMoves[2][field][1] & (board.pieceBitboards[4] | board.pieceBitboards[1]) & enemy), (allMoves[3][field][1] & (board.pieceBitboards[4] | board.pieceBitboards[3]) & enemy))
    if np.any(attackerPieces):
        for n in nonzeroElements(attackerPieces):
            blockers = between[field][toNumber(n)] & all
            if not blockers:
                return (between[field][toNumber(n)] | n)
    return np.uint64(0)


def inCheck(board, color: np.uint64, enemy: np.uint64, white: bool, all):
    kingN = nonzeroElements(board.pieceList[5] & color)
    return attacked(board, enemy, white, kingN, all)

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

def nonzeroElements(array: np.ndarray):
    return array[np.nonzero(array)]

def pinned(board, color: np.uint64, enemy: np.uint64):
    king = np.max(board.pieceList[5] & color)
    kNumber = toNumber(king)
    attackers = np.append((allMoves[2][kNumber][1] & (np.bitwise_or.reduce(board.pieceList[4]) | np.bitwise_or.reduce(board.pieceList[1])) & enemy), (allMoves[3][kNumber][1] & (np.bitwise_or.reduce(board.pieceList[4]) | np.bitwise_or.reduce(board.pieceList[3])) & enemy))
    pinned = np.uint64(0)
    for n in nonzeroElements(attackers):
        blockers = between[kNumber][toNumber(n)] & board.all
        if popcount_zero(blockers) == 1:
            pinned |= blockers & color
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
    return False

def checkmate(board):
    if board.isWhite:
        color = board.white
        enemy = board.black
    else:
        enemy = board.white
        color = board.black
    return (board.moves == [] and inCheck(board, color, enemy, board.isWhite, board.all))

def remis(board):
    return (board.halfmove == 50 or board.moves == [])

def now():
    return time.time()*1000

def iterativeDeepening(timeLimit, board, alpha, beta, maximizingPlayer, list):
    endTime = now() + timeLimit
    depth = 1
    result = 0
    while True:
        if now() >= endTime:
            break
        result = alphabeta(board, depth, alpha, beta, maximizingPlayer, list)
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


def alphabeta(board, depth, alpha, beta, maximizingPlayer, list):
    #objFound = board.getEntry()
    #if objFound is not None:
    #    if objFound.get('lowerbound', float('-inf'))>= beta:
    #         return objFound['lowerbound']
    #    if objFound.get('upperbound', float('inf')) <= alpha:
    #         return objFound['upperbound']
    #    alpha = max(alpha, objFound.get('lowerbound', float('-inf')))
    #    beta = min(beta, objFound.get('upperbound', float('inf')))
    if depth == 0 or isGameDone(board):
        value = evalBoard(board)
        if len(board.moveHistoryAB) > 0:
            move = board.moveHistoryAB.pop()
            list.append((move, value))
            board.undoMove(move)
        return value
    if maximizingPlayer:
        value = float('-inf')
        for child in board.getMoves():
            value = max(value, alphabeta(board.doMove(child), depth-1, alpha, beta, False,list))
            if len(board.moveHistoryAB) > 0:
                move = board.moveHistoryAB.pop()
                list.append((move, value))
                board.undoMove(move)
            if value >= beta:
                break
            alpha = max(alpha, value)
    else:
        value = float('inf')
        for child in board.getMoves():
            value = min(value, alphabeta(board.doMove(child), depth-1, alpha, beta, True, list ))
            if len(board.moveHistoryAB) > 0:
                move = board.moveHistoryAB.pop()
                list.append((move, value))
                board.undoMove(move)
            if value <= alpha:
                break
            beta = min(beta, value)

    #if value <= alpha:
    #    id = board.getHash()
    #    board.ttable.update({id: {'upperbound': value}})
    #if value > alpha and value < beta:
    #    id = board.getHash()
    #    board.ttable.update({id: {'lowerbound': value, 'upperbound': value}})
    #if value >= beta:
    #    id = board.getHash()
    #    board.ttable.update({id: {'lowerbound': value}})
    return value



def evalBoard(board):
    color = board.white
    enemy = board.black
    if not board.isWhite:
        color = board.black
        enemy = board.white
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
    check = 0
    #if inCheck(board, enemy, color, not board.isWhite,board.all):
    #    check = 1
    ##check = inCheck(board, enemy, color, not board.isWhite,board.all) - \
    ##    inCheck(board, color, enemy, board.isWhite,board.all)
    # TODO 1: include  checkmate (very high value), king of the hill (very high value), remis (negative value)
    # TODO 2: implement multiple evaluation functions => z.B. Ruhesuche bei vielen Figuren
    return 10 * check + 9 * queenDelta + 5 * rookDelta + 3 * knightDelta + 3 * bishopDelta + 1 * pawnDelta


def movesToJSON(moves):
    list = []
    for move in moves:
        value = move[1]
        move = move[0][0]
        object = {}
        object['fromField'] = fieldToString(move[0])
        object['toField'] = fieldToString(move[1])
        object['figure'] = getFigure(move[2])
        object['enPassant'] = bool(move[3])
        object['castle'] = bool(move[4])
        object['promotion'] = bool(move[5])
        object['value'] = value
        list.append(object)
    return {'moves': list}

def popcount_zero(x):
    c = 0
    while x:
        x &= x - np.uint(1)
        c += 1
    return c