from Board import *
from utils import toFen, toNumber, movesToJSON, iterativeDeepening
from copy import deepcopy

board  = Board('rnbqkbnr/pppppppp/8/8/8/8/PPPPPPPP/RNBQKBNR w KQkq - 0 1')

def initBoard(fenString):
    global board
    board = Board(fenString)
    return getMoves()

def getMoves():
    result = []
    iterativeDeepening(500, board, -10000, 10000, False, result)
    return movesToJSON(result)

def testMoves():
    b = board
    for i in range(10):
        print(toFen(b))
        moves = b.getMoves()
        b.doMove(moves[0])
    return {'test':'ok'}

def doMove(move):
    fromField= toNumber(move['fromField'])
    toField= toNumber(move['toField'])
    figure = toNumber(move['figure'])
    enPassant = bool(move['enPassant'])
    castle = bool(move['castle'])
    promotion = bool(move['promotion'])
    board.doMove((fromField, toField, figure, enPassant, castle, promotion))
    return 200

    