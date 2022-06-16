from Board import *
from utils import toFen, toNumber, movesToJSON2, alphaBetaMove

board  = Board('8/8/5k2/8/8/2K5/8/8 w - - 0 1')

def initBoard(fenString):
    global board
    board = Board(fenString)
    return getMoves()

def getMoves():
    return movesToJSON2(alphaBetaMove(board, 3, -10000, 10000, True))

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

    