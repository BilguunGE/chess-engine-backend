from time import time
from helpers import *

# //////////////////////////////////////////////////////
#
#                    Next Move
#
# //////////////////////////////////////////////////////

bestMoves = []

# //////////////////////////////////////////////////////
#
#                    Algorithms
#
# //////////////////////////////////////////////////////

def minimax(board, depth, isMax, playerAtMoveFactor, shouldSave):
    global bestMoves
    if (depth == 0) or board.isGameDone():
        return playerAtMoveFactor * board.evaluate() * (1.1**depth)
    if isMax:
        value = float('-inf')
        for move in board.getMoves():
            board.doMove(move)
            score = minimax(board, depth-1, 0, -playerAtMoveFactor, 0)
            value = max(value, score)
            board.undoLastMove()
            if shouldSave:
                bestMoves.append({ 'move': move, 'value': score})
        return value
    else:
        value = float('inf')
        for move in board.getMoves():
            board.doMove(move)
            value = min(value, minimax(board, depth-1, 1,-playerAtMoveFactor, 0))
            board.undoLastMove()
        return value    
        
def alphaBeta(board, depth, alpha, beta, isMax, playerAtMoveFactor, shouldSave, stopTime):
    global bestMoves
    if time() * 1000 - 500 >= stopTime:
        timeFactor = 1
        if isMax:
            timeFactor = -1
        return timeFactor * playerAtMoveFactor * 10000
    hash = board.genZobHash()
    if hash in board.ttable:
        print("already known state!")
        if board.ttable[hash]["depth"] >= depth:
            return board.ttable[hash]["value"]
    if (depth == 0) or board.isGameDone():
        return playerAtMoveFactor * board.evaluate() * (1.1**depth)
    if isMax:
        value = alpha
        for move in board.getMoves():
            board.doMove(move)
            score = alphaBeta(board, depth - 1, value, beta, 0, -playerAtMoveFactor, 0, stopTime)
            value = max(value, score)
            board.undoLastMove()
            if shouldSave:
                bestMoves.append({ "move": move, "value": score })
            if value >= beta:
                break
        board.ttable[hash] = {"depth":depth, "value":value}
        return value
    else:
        value = beta
        for move in board.getMoves():
            board.doMove(move)
            value = min(value, alphaBeta(board, depth - 1, alpha, value, 1, -playerAtMoveFactor, 0, stopTime))
            board.undoLastMove()
            if value <= alpha:
                break
        board.ttable[hash] = {"depth":depth, "value":value}
        return value
        