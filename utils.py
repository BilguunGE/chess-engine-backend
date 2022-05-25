import numpy as np
from moves import *

def fieldToString(field: np.uint64):
    field = np.ceil(np.log2(field)).astype(int)
    y = field%8
    x = (field - y) / 8
    print(y)
    txt = 'abcdefgh'[int(7-x)] + '12345678'[int(y)]
    return txt

def toNumber(field):
    field = np.ceil(np.log2(field)).astype(int)
    return field

def bits(fields: np.uint64):
    while fields:
        b = fields & (~fields+np.uint64(1))
        yield toNumber(b) - np.uint64(1)
        fields ^= b

def attacked(board,enemy,white,field):
    attackers = np.array([],dtype=np.uint64)
    if np.any(enemy & board.knight & allMoves[5][field][2]):
        x = enemy & board.knight & allMoves[5][field][2]
        attackers = np.append(attackers, x[np.nonzero(x)])
    if np.any(enemy & board.king & allMoves[4][field][2]):
        x = np.any(enemy & board.king & allMoves[4][field][2])
        attackers = np.append(attackers, x[np.nonzero(x)])
    if np.any(white and (enemy & board.pawn & allMoves[0][field][2][1])):
        x = enemy & board.pawn & allMoves[0][field][2][1]
        attackers = np.append(attackers, x[np.nonzero(x)])
    if np.any(not white and (enemy & board.pawn & allMoves[1][field][2][1])):
        x = enemy & board.pawn & allMoves[1][field][2][1]
        attackers = np.append(attackers, x[np.nonzero(x)])
    attackerPieces = (allMoves[2][field][2] & (board.queen | board.rook) & enemy) | (allMoves[3][field][2] & (board.queen | board.bishop) & enemy) 
    if np.any(attackerPieces):
        if x:
            blockers = between[field][toNumber(x)] & board.all
        if not blockers:
            attackers = np.append(x)
    return np.uint64(0)

def inCheck(board,color,enemy,white):
    kingN = np.max(board.king & color)
    return attacked(board,enemy,white,toNumber(kingN))