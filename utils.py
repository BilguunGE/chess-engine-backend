import numpy as np
from moves import *

def fieldToString(field: np.uint64):
    field = np.ceil(np.log2(field)).astype(int)
    y = field%8
    x = (field - y) / 8
    print(y)
    txt = 'abcdefgh'[int(7-x)] + '12345678'[int(y)]
    return txt

def toNumber(field: np.uint64):
    field = np.ceil(np.log2(field)).astype(int)
    return field

def bits(fields: np.uint64):
    while fields:
        b = fields & (~fields+np.uint64(1))
        yield toNumber(b) - np.uint64(1)
        fields ^= b

def attacked(board,enemy,white,field):
    if np.all(enemy & board.knight & allMoves[5][field][2]):
        return enemy & board.knight & allMoves[5][field][2]
    if np.all(enemy & board.king & allMoves[4][field][2]):
        return enemy & board.king & allMoves[4][field][2]
    if np.all(white and (enemy & board.pawn & allMoves[0][field][2][1])):
        return enemy & board.pawn & allMoves[0][field][2][1]
    if np.all(not white and (enemy & board.pawn & allMoves[1][field][2][1])):
        return enemy & board.pawn & allMoves[1][field][2][1]
    attackers = (allMoves[2][field][2] & (board.queen | board.rook) & enemy) | (allMoves[3][field][2] & (board.queen | board.bishop) & enemy) 
    for i in attackers:
        if i:
            blockers = between[field][toNumber(i)] & board.all
        if not blockers:
            return i
    return np.uint64(0)

def inCheck(board,color,enemy,white):
    kingN = board.king & color
    return attacked(board,enemy,white,kingN.bit_length() - 1)