from Board import Board


def getMoves(fenString):
    board = Board(fenString)
    moves = board.getMovesW()
    return {'moves': moves}
    