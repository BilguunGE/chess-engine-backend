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
    moves = board.getMoves()
    if (depth == 0) or board.isGameDone():
        return playerAtMoveFactor * board.evaluate() * (1.1**depth)
    if isMax:
        value = float('-inf')
        for move in moves:
            board.doMove(move)
            score = minimax(board, depth-1, 0, -playerAtMoveFactor, 0)
            value = max(value, score)
            board.undoLastMove()
            if shouldSave:
                bestMoves.append({ 'move': move, 'value': score})
        return value
    else:
        value = float('inf')
        for move in moves:
            board.doMove(move)
            value = min(value, minimax(board, depth-1, 1,-playerAtMoveFactor, 0))
            board.undoLastMove()
        return value    
        
def alphaBeta(board, depth, alpha, beta, isMax, shouldSave, stopTime, counter={"count":0}):
    counter["count"] += 1
    if isTimeUp(stopTime): print("Time up!!!")
    if isMax:
        minmaxFactor = 1
    else:
        minmaxFactor = -1
    if (depth == 0) or board.isGameDone() or isTimeUp(stopTime):
        return minmaxFactor * board.evaluate() * (1.1**depth)
    moves = board.getMoves()
    if isMax:
        value = alpha
        for move in moves:
            board.doMove(move)
            hash = board.genZobHash()
            if hash in board.ttable:
                if board.ttable[hash]["depth"]>=depth-1:
                    #GET
                    score = board.ttable[hash]["score"]
                else:
                    #UPDATE
                    score = alphaBeta(board, depth - 1,value, beta, 0, 0, stopTime, counter)
                    if isTimeUp(stopTime):
                        score = board.ttable[hash]["score"]
                    else:
                        board.ttable[hash] = { "score" : score, "depth" : depth-1, "move" : move }
            else:
                #CREATE
                score = alphaBeta(board, depth - 1, value, beta, 0, 0, stopTime, counter) 
                if not (isTimeUp(stopTime)):
                    board.ttable[hash] = { "score" : score, "depth" : depth-1, "move" : move }
            value = max(value, score)
            board.undoLastMove()
            if shouldSave:
                bestMoves.append({ "move": move, "value": score })
            if value >= beta:
                break
        return value
    else:
        value = beta
        for move in moves:
            board.doMove(move)
            hash = board.genZobHash()
            if hash in board.ttable:
                if board.ttable[hash]["depth"]>=depth-1:
                    #GET
                    score = board.ttable[hash]["score"]
                else:
                    #UPDATE
                    score = alphaBeta(board, depth - 1, alpha, value, 1, 0, stopTime, counter)
                    if isTimeUp(stopTime):
                        score = board.ttable[hash]["score"]
                    else:
                        board.ttable[hash] = { "score" : score, "depth" : depth-1, "move" : move }
            else:
                #CREATE
                score = alphaBeta(board, depth - 1, alpha, value, 1, 0, stopTime, counter) 
                if not (isTimeUp(stopTime)):
                    board.ttable[hash] = { "score" : score, "depth" : depth-1, "move" : move }
            value = min(value, score)
            board.undoLastMove()
            if value <= alpha:
                break
        return value

def alphaBetaNoHash(board, depth, alpha, beta, isMax, shouldSave, counter={"count":0}):
    counter["count"] += 1
    if isMax:
        minmaxFactor = 1
    else:
        minmaxFactor = -1
    if (depth == 0) or board.isGameDone():
        return minmaxFactor * board.evaluate() * (1.1**depth)
    moves = board.getMoves()
    if isMax:
        value = alpha
        for move in moves:
            board.doMove(move)
            score = alphaBetaNoHash(board, depth - 1, value, beta, 0, 0, counter) 
            value = max(value, score)
            board.undoLastMove()
            if shouldSave:
                bestMoves.append({ "move": move, "value": score })
            if value >= beta:
                break
        return value
    else:
        value = beta
        for move in moves:
            board.doMove(move)
            score = alphaBetaNoHash(board, depth - 1, alpha, value, 1, 0, counter) 
            value = min(value, score)
            board.undoLastMove()
            if value <= alpha:
                break
        return value