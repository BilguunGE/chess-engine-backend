from operator import itemgetter
from time import time
from helpers import *
    
def minimax(board,depth):
    nextMoves = []
    if depth <= 0:
        return 
    start = time()
    isWhite = board.isWhiteTurn
    moves = board.getMoves()
    
    for move in moves:
        board.doMove(move)
        nextMoves.append({
            "move": move,
            "value": minimaxAlgorithm(board, depth - 1, False, isWhite)
        })
        board.undoLastMove()
    end = time()
    print("Minimax took "+ str(end - start)+ " seconds.")
    highestVal = max(nextMoves, key=itemgetter("value"))["value"]
    bestMoves = []
    for move in nextMoves:
        if move["value"] == highestVal:
            bestMoves.append(move)
    return pickRandom(bestMoves)

def minimaxAlgorithm(board, depth, isMax, isWhiteAtRoot):
    if depth == 0 or board.isGameDone():
        colorFactor = -1
        if board.isWhiteTurn and isWhiteAtRoot:
            colorFactor = 1
        return colorFactor * board.evaluate() * (1.1**depth)    
    if isMax:
        value = float('-inf')
        for move in board.getMoves():
            board.doMove(move)
            value = max(value, minimaxAlgorithm(board, depth-1, False, isWhiteAtRoot))
            board.undoLastMove()
        return value
    else:
        value = float('inf')
        for move in board.getMoves():
            board.doMove(move)
            value = min(value, minimaxAlgorithm(board, depth-1, True, isWhiteAtRoot))
            board.undoLastMove()
        return value
    
        
def alphaBeta(board,depth):
    # might switch to single move approach for bigger cutoff effect
    nextMoves = []
    if depth <= 0:
        return 
    start = time()
    isWhite = board.isWhiteTurn
    moves = board.getMoves()
    for move in moves:
        board.doMove(move)
        value = alphaBetaAlgorithm(board, depth - 1, -10000,10000, False, isWhite)
        nextMoves.append({
            "move": move,
            "value": value
        })
        board.undoLastMove()
        if value >= 10000:
            break
    end = time()
    print("AlphaBeta took "+ str(end - start)+ " seconds.")
    highestVal = max(nextMoves, key=itemgetter("value"))["value"]
    bestMoves = []
    for move in nextMoves:
        if move["value"] == highestVal:
            bestMoves.append(move)
    return pickRandom(bestMoves)

def alphaBetaAlgorithm(board, depth, alpha, beta, isMax, isWhiteAtRoot):
    moves = board.getMoves()
    if (depth == 0) or board.isGameDone():
        colorFactor = -1
        if board.isWhiteTurn and isWhiteAtRoot:
            colorFactor = 1
        return colorFactor * board.evaluate() * (1.1**depth)
    if isMax:
        value = alpha
        for move in moves:
            board.doMove(move)
            value = max(value, alphaBetaAlgorithm(board, depth - 1, value, beta, False, isWhiteAtRoot))
            board.undoLastMove()
            if value >= beta:
                break
        return value
    else:
        value = beta
        for move in moves:
            board.doMove(move)
            value = min(value, alphaBetaAlgorithm(board, depth - 1, alpha, value, True, isWhiteAtRoot))
            board.undoLastMove()
            if value <= alpha:
                break
        return value
