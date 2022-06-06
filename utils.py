from typing import Union
import numpy as np
from moves import *
import math
import time


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

def bits(fields: np.uint64):
    binary = bin(fields)
    indices = np.array([i for i, c in enumerate(binary) if c == '1'])
    return 63 - (indices - 2)

def attacked(board, enemy: np.ndarray,white: bool,field: np.uint64):
    field = np.max(toNumber(field))
    if np.any(enemy & board.pieceList[2] & allMoves[5][field][2]):
        return np.max(enemy & board.pieceList[2] & allMoves[5][field][2])
    if np.any(enemy & board.pieceList[5] & allMoves[4][field][2]):
        return np.max(enemy & board.pieceList[5] & allMoves[4][field][2])
    if np.any(white and np.any(enemy & board.pieceList[0] & allMoves[0][field][2][1])):
        return np.max(enemy & board.pieceList[0] & allMoves[0][field][2][1])
    if np.any(not white and np.any(enemy & board.pieceList[0] & allMoves[1][field][2][1])):
        return np.max(enemy & board.pieceList[0] & allMoves[1][field][2][1])
    attackerPieces = np.append((allMoves[2][field][1] & (np.bitwise_or.reduce(board.pieceList[4]) | np.bitwise_or.reduce(board.pieceList[1])) & enemy), (allMoves[3][field][1] & (np.bitwise_or.reduce(board.pieceList[4]) | np.bitwise_or.reduce(board.pieceList[3])) & enemy))
    if np.any(attackerPieces):
        for n in nonzeroElements(attackerPieces):
            blockers = between[field][toNumber(n)] & board.all
            if not blockers:
                return (between[field][toNumber(n)] | n)
    return np.uint64(0)

def inCheck(board, color: np.uint64,enemy: np.uint64,white: bool):
    kingN = nonzeroElements(board.pieceList[5] & color)
    return attacked(board,enemy,white,kingN)

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
        if blockers.bit_count() == 1:
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

def evalBoard(board):
    return 0

def now():
    return time.time()*1000

def iterativeDeepening(timeLimit, board, depth, alpha, beta, maximizingPlayer):
    endTime = now() + timeLimit
    depth = 1
    result = 0
    while True:
        if now() >= endTime:
            break
        result = alphabeta(board, depth, alpha, beta, maximizingPlayer)
        depth += 1
    return result

def minimax(board, depth, maximizingPlayer):
    if depth == 0 or isGameDone(board):
        value = evalBoard(board)
        board.undoAllMoves()
        return value
    if maximizingPlayer:
        value = float('-inf')
        for child in board.getMoves():
            value = math.max(value, minimax(board.doMove(child), depth-1, False))
        return value
    else:
        value = float('inf')
        for child in board.getMoves():
            value = math.min(value, minimax(board.doMove(child), depth-1, True))
        return value


def alphabeta(board, depth, alpha, beta, maximizingPlayer):
    if depth == 0 or isGameDone(board):
        value = evalBoard(board)
        board.undoAllMoves()
        return value
    if maximizingPlayer:
        value = float('-inf')
        for child in board.getMoves():
            value = math.max(value, alphabeta(board.doMove(child), depth-1, alpha, beta, False))
            if value >= beta:
                break
            alpha = math.max(alpha, value)
        return value
    else:
        value = float('inf')
        for child in board.getMoves():
            value = math.min(value, alphabeta(board.doMove(child), depth-1, alpha, beta, True))
            if value <= alpha:
                break
            beta = math.min(beta, value)
        return value