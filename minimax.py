from helpers import *
from Board import *

def minimax(board: Board, depth, isMax, playerAtMoveFactor, shouldSave):
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
                board.best_moves.append({ 'move': move, 'value': score})
        return value
    else:
        value = float('inf')
        for move in moves:
            board.doMove(move)
            value = min(value, minimax(board, depth-1, 1,-playerAtMoveFactor, 0))
            board.undoLastMove()
        return value    
        
def alphaBeta(board: Board, depth, alpha, beta, isMax, shouldSave, stopTime, counter={"count":0}):
    counter["count"] += 1
    hash = board.genZobHash()
    isHashed = hash in board.ttable
    if isHashed:
        if board.ttable[hash]["depth"] >= depth:
            best_moves = board.ttable[hash]["moves"]
            score = board.ttable[hash]["score"]
            if shouldSave:
                board.best_moves = best_moves
            return score
    moves = board.getMoves()
    isGameDone = board.isGameDone() > 0
    if (depth == 0) or isGameDone or isTimeUp(stopTime):
        return board.evaluate(isMax)
    best_moves = []
    if isMax:
        value = alpha
        for move in moves:
            board.doMove(move)
            score = alphaBeta(board, depth - 1,value, beta, 0, 0, stopTime, counter)   
            if value == score:
                best_moves.append(move)
            elif value < score:
                value = score
                best_moves = []
                best_moves.append(move) 
            board.undoLastMove()
            if value >= beta:
                break
        if not isTimeUp(stopTime):
            board.ttable[hash] = { "score" : value, "depth" : depth, "moves" : best_moves }
        if shouldSave:
            board.best_moves = best_moves
        return value
    else:
        value = beta
        for move in moves:
            board.doMove(move)
            score = alphaBeta(board, depth - 1, alpha, value, 1, 0, stopTime, counter)
            if value == score:
                best_moves.append(move)
            elif value > score:
                value = score
                best_moves = []
                best_moves.append(move) 
            board.undoLastMove()
            if value <= alpha:
                break
        if not isTimeUp(stopTime):
            board.ttable[hash] = { "score" : value, "depth" : depth, "moves" : best_moves }
        return value

def alphaBetaNoHash(board: Board, depth, alpha, beta, isMax, shouldSave, counter={"count":0}):
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
                board.best_moves.append({ "move": move, "value": score })
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