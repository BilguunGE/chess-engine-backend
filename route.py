from Board import Board


def getMoves(fenString):
    board = Board(fenString)
    moves = board.getMovesW()
    result = []
    for move in moves:
        result.append({'move': move})
    return {'moves': result}
    