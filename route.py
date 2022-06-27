from Board import *
from utils import toFen, toNumber, movesToJSON2, alphaBetaMove

# board  = Board('rnbqkbnr/pppppppp/8/8/8/8/PPPPPPPP/RNBQKBNR w KQkq - 0 1')
board  = Board('8/6k1/8/8/8/8/1K6/8 w - - 0 1')

# TODO Bug
def initBoard(fenString):
    print("Executing initBoard")
    global board
    board = Board(fenString)
    print("Initiated board: ", toFen(board), "("+fenString+")")
    print(board.getMoves())
    return getMoves()

def getMoves():
    return movesToJSON(board.getMoves())

def alphaBeta():
    return { "result" : alphaBetaMove(board, 6, -10000, 10000) }

def testMoves():
    b = board
    for i in range(10):
        print(toFen(b))
        moves = b.getMoves()
        b.doMove(moves[0])
    return {'test':'ok'}

def doMove(move):
    print("Executing doMove")
    fromField= toNumber(move['fromField'])
    toField= toNumber(move['toField'])
    figure = toNumber(move['figure'])
    enPassant = bool(move['enPassant'])
    castle = bool(move['castle'])
    promotion = bool(move['promotion'])
    board.doMove((fromField, toField, figure, enPassant, castle, promotion))
    return 200

    