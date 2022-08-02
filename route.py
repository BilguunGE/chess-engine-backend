from Board import *
from helpers import *
from algorithms import *
from mcts import MCTS

current_board  = Board('rnbqkbnr/pppppppp/8/8/8/8/PPPPPPPP/RNBQKBNR w KQkq - 0 1')

def initBoard(fenString):
    print("Executing initBoard")
    global current_board
    current_board = Board(fenString)
    print("Initiated current_board: \n" + getBoardStr(current_board) + "\n("+fenString+")\n")
    return {"board" : fenString}

def getMoves():
    return {"moves" : list(map(getMoveToString, current_board.getMoves()))}

def alphaBetaMove(depth, alpha, beta, stopTime, useNN):
    print("Executing alpha beta")
    bestMoves.clear()
    start = time()
    alphaBeta(current_board,depth, alpha, beta, 1, 1, stopTime, useNN)
    print("Depth "+str(depth) + " took " + str(time()-start) + " seconds")
    printBestMoves(bestMoves)
    bestMove = pickRandomBest(bestMoves)
    return { "move" : bestMove["move"]["toString"], "value": bestMove["value"], "depth":depth }

def mctsMove(moves, endTime):
    move = MCTS().findNextMove(current_board, endTime, moves)
    return { "move" : move[0]['toString'], "winScore":move[1] }

    