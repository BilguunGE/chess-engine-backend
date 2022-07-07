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
        
# def alphaBeta(board, depth, alpha, beta, isMax, playerAtMoveFactor, shouldSave, stopTime):
#     global bestMoves
#     if time() * 1000 - 500 >= stopTime:
#         timeFactor = 1
#         if isMax:
#             timeFactor = -1
#         return timeFactor * playerAtMoveFactor * 10000
#     hash = board.genZobHash()
#     if hash in board.ttable:
#         print("already known state!")
#         if board.ttable[hash]["depth"] >= depth:
#             return board.ttable[hash]["value"]
#     if (depth == 0) or board.isGameDone():
#         return playerAtMoveFactor * board.evaluate() * (1.1**depth)
#     if isMax:
#         value = alpha
#         for move in board.getMoves():
#             board.doMove(move)
#             score = alphaBeta(board, depth - 1, value, beta, 0, -playerAtMoveFactor, 0, stopTime)
#             value = max(value, score)
#             board.undoLastMove()
#             if shouldSave:
#                 bestMoves.append({ "move": move, "value": score })
#             if value >= beta:
#                 break
#         board.ttable[hash] = {"depth":depth, "value":value}
#         return value
#     else:
#         value = beta
#         for move in board.getMoves():
#             board.doMove(move)
#             value = min(value, alphaBeta(board, depth - 1, alpha, value, 1, -playerAtMoveFactor, 0, stopTime))
#             board.undoLastMove()
#             if value <= alpha:
#                 break
#         board.ttable[hash] = {"depth":depth, "value":value}
#         return value

def alphaBeta(board, depth, alpha, beta, isMax, playerAtMoveFactor, shouldSave):
    global bestMoves
    # if time() * 1000 - 500 >= stopTime:
    #     timeFactor = 1
    #     if isMax:
    #         timeFactor = -1
    #     return timeFactor * playerAtMoveFactor * 10000

    hash = board.hash
    if board.ttable.get(hash):
        print("already known state!",hash)
        objFound = board.ttable.get(hash)
        if objFound.get('lowerbound') and objFound.get('lowerbound')>= beta and objFound.get('age')>=depth:
             return objFound['lowerbound']
        if objFound.get('upperbound') and objFound.get('upperbound') <= alpha and objFound.get('age')>=depth:
             return objFound['upperbound']
        if objFound.get('lowerbound'):
            alpha = max(alpha, objFound.get('lowerbound'))
        if objFound.get('lowerbound'):
            beta = min(beta, objFound.get('upperbound'))

    moves = board.getMoves()
    if (depth == 0) or board.isGameDone():
        return playerAtMoveFactor * board.evaluate() * (1.1**depth)

    if isMax:
        value = alpha
        for move in moves:
            board.doMove(move)
            score = alphaBeta(board, depth - 1, value, beta, 0, -playerAtMoveFactor, 0)
            value = max(value, score)
            board.undoLastMove()
            if shouldSave:
                bestMoves.append({ "move": move, "value": score })
            if value >= beta:
                break
    else:
        value = beta
        for move in moves:
            board.doMove(move)
            value = min(value, alphaBeta(board, depth - 1, alpha, value, 1, -playerAtMoveFactor, 0))
            board.undoLastMove()
            if value <= alpha:
                break

    if value <= alpha:
        board.ttable.update({hash: {'upperbound': value, 'age': depth}})
    if value > alpha and value < beta:
        board.ttable.update({hash: {'lowerbound': value, 'upperbound': value, 'age':depth}})
    if value >= beta:
        board.ttable.update({hash: {'lowerbound': value, 'age': depth}})
    return value

def iterativeDeepening(board, alpha, beta, stopTime):
     depth = 1
     result = 0
     while time()*1000 < stopTime:
         result = alphaBeta(board, depth, alpha, beta, 1 , 1 , 1, stopTime)
         depth += 1
     return (result, depth)
        