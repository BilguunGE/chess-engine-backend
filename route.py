from Board import Board


def getMoves(fenString):
    board = Board(fenString)
    moves = board.getMoves()
    return {'moves': moves}
    