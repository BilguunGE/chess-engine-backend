from Board import *
from utils import fieldToString, getFigure
from evaluation import evaluate


def getMoves(fenString):
    b = Board(fenString)
    moves = b.getMoves()
    list = []
    for move in moves:
        object = {}
        figure = getFigure(move[2], b.isWhite)
        fromField = fieldToString(move[0])
        beat = isBeat(move[3])
        toField = fieldToString(move[1])
        object['toString'] = figure + fromField+beat+toField
        object['isHit'] = bool(move[3])
        list.append(object)
    return {
        'moves': list, 
        'value': evaluate(b)
        }
