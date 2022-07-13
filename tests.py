from time import time
from Board2 import *
from helpers import *
from algorithms import *

# //////////////////////////////////////////////////////
#
#                    Test functions
#
# //////////////////////////////////////////////////////

def checkMoveGenSpeed(board, iterations):
    i = 0
    list = []
    while i < iterations:
        start = time()
        board.getMoves()
        end = time()
        list.append(end - start)
        i +=1
    print(str((sum(list)*1000)/len(list))+"ms")
    
    


def testDoUndo(board, moveAmount):
    #TODO check all properties like castle, en passant etc.
    before = getBoardStr(board)
    i = 0
    while i < moveAmount:
        moves = board.getMoves()
        if len(moves)>0:
            randomIndex = randint(0,len(moves)-1)
            board.doMove(moves[randomIndex])
        i = i + 1
    i = 0
    while i < moveAmount:
        board.undoLastMove()
        i = i + 1
        
    after = getBoardStr(board)
    print(before)
    print(after)


# //////////////////////////////////////////////////////
#
#                    Scenarios
#
# //////////////////////////////////////////////////////

startGame = Board('rnbqkbnr/pppppppp/8/8/8/8/PPPPPPPP/RNBQKBNR w KQkq - 0 1')
midGame = Board('r1br2k1/pppp1pp1/7p/2b1p3/2Pn4/4QN2/PP2PPBP/RN3RK1 w - - 0 1')
endGame = Board('8/p3k3/5N2/4P3/8/B7/8/K7 b - - 0 1')
firstOnTheHill  = Board('8/6k1/8/8/8/8/1K6/8 w - - 0 1')

# //////////////////////////////////////////////////////
#
#                    Tests
#
# //////////////////////////////////////////////////////

start = time()

#insert test

print(f"\nTest took {time() - start} seconds.\n")