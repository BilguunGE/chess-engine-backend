from Board import *
from utils import fieldToString, getFigure


def getMoves(fenString):
    b = Board(fenString)
    moves = b.getMoves()
    list = []
    for move in moves:
        object = {}
        object['fromField'] = fieldToString(move[0])
        object['toField'] = fieldToString(move[1])
        object['figure'] = getFigure(move[2])
        object['enPassant'] = bool(move[3])
        list.append(object)
    return {'moves': list}
