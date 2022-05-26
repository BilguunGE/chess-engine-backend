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

def toFen(board):
    boardTxt = ['-']*64
    for n in board.pawn:
        boardTxt[toNumber(n)] = 'p'
    for n in board.rook:
        boardTxt[toNumber(n)] = 'r'
    for n in board.knight:
        boardTxt[toNumber(n)] = 'n'
    for n in board.bishop:
        boardTxt[toNumber(n)] = 'b'
    for n in board.queen:
        boardTxt[toNumber(n)] = 'q'
    for n in board.king:
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

    if board.player:
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
        i = toNumber(board.en_passant)
        y = (i % 8)
        x = 8 - ((i - y) / 8)
        fen += chr(y + 97) + str(x)
    else:
        fen += '-'
    fen += ' '

    fen += str(board.halfmove) + ' ' + str(board.fullmove)
    return fen