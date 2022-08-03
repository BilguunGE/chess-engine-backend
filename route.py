from Board import *
from helpers import *
from minimax import *
from constants import *
from mcts import MCTS

class GameState:    
    def __init__(self): 
        self.current_board = Board('rnbqkbnr/pppppppp/8/8/8/8/PPPPPPPP/RNBQKBNR w KQkq - 0 1')

    def initBoard(self, fenString):
        print("Executing initBoard")
        self.current_board = Board(fenString)
        print("Initiated game_state: \n" + getBoardStr(self.current_board) + "\n("+fenString+")\n")
        return {"board" : fenString}

    def getMoves(self):
        return {"moves" : list(map(getMoveToString, self.current_board.getMoves()))}

    def alphaBetaMove(self, depth, stopTime):
        print("Executing alpha beta")
        self.current_board.best_moves = []
        start = time()
        value = alphaBeta(self.current_board, depth, ALPHA_START, BETA_START, 1, 1, stopTime)
        print("Depth "+str(depth) + " took " + str(time()-start) + " seconds")
        return { "moves" : self.current_board.best_moves, "value": value, "depth":depth }
    
    
    def mctsMove(self, stopTime):
        print("Executing MCTS")
        bestMoveCount = len(self.current_board.best_moves)
        if (bestMoveCount <= 0):
            return {"info": "no best moves available"}
        elif (bestMoveCount == 1):
            return {"move": self.current_board.best_moves[0]}
        elif bestMoveCount > 1:         
            move = MCTS().findNextMove(self.current_board, stopTime/1000, list(map(getMoveToString, self.current_board.best_moves)))
            return { "move" : move[0] }
    
    def doMove(self, move):
        self.current_board.doMove(move)
        return {"board": self.current_board.getFEN()}   
    
    def undoLastMove(self):
        self.current_board.undoLastMove()
        return {"board": self.current_board.getFEN()}   
    