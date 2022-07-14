from time import time
from Board2 import *
from helpers import *
from algorithms import *

# //////////////////////////////////////////////////////
#
#                    Test functions
#
# //////////////////////////////////////////////////////

def testMoveGenSpeed(board, iterations):
    i = 0
    list = []
    while i < iterations:
        start = time()
        board.getMoves()
        list.append(time() - start)
        i +=1
    print(str((sum(list)*1000)/len(list))+"ms")
    
    
def testAlphaBeta(board, depth, stopTime, iterations):
    i = 0
    list = []
    while i< iterations:
        start = time()
        alphaBeta(board,depth,-10000,10000,1,1,stopTime)
        list.append(time()-start)
        i += 1
    print(str((sum(list)*1000)/len(list))+"ms")
    
def testAlphaBetaNewTT(fen, depth, stopTime, iterations):
    i = 0
    list = []
    while i< iterations:
        board = Board(fen)
        start = time()
        alphaBeta(board,depth,-10000,10000,1,1,stopTime)
        list.append(time()-start)
        i += 1
    print(str((sum(list)*1000)/len(list))+"ms")
    
def testAlphaBetaNoHash(board, depth, iterations):
    i = 0
    list = []
    while i< iterations:
        start = time()
        alphaBetaNoHash(board,depth,-10000,10000,1,1)
        list.append(time()-start)
        i += 1
    print(str((sum(list)*1000)/len(list))+"ms")


def testDoUndo(board, moveAmount):
    before = getBoardStr(board)
    beforeFen = board.fenString
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
    print(beforeFen)
    print()
    print(after)
    print("isWhite: ", board.isWhiteTurn)
    print("castleRight: ", board.castleRight)
    print("enPassant: ", board.enPassant)
    print("half: ", board.halfmoveClock)
    print("full: ", board.fullmoveCount)
    
# //////////////////////////////////////////////////////
#
#                Project Benchmarks
#
# //////////////////////////////////////////////////////

def mst3(boards, maxDepth, iterations):
    for board in boards:
        depth = 1
        print(f"\nState: {board.fenString}")
        while depth <= maxDepth:
            i = 0
            valueList = []
            timeList = []
            state_countList = []
            stateCount = {"count":0}
            while i < iterations:
                bestMoves.clear()
                start = time()
                # value = alphaBeta(board, depth, -10000, 10000, 1, 1, time()*1000+120000,stateCount )
                value = alphaBetaNoHash(board, depth, -10000, 10000, 1, 1, stateCount)
                timeList.append(time()-start)
                valueList.append(value)
                state_countList.append(stateCount["count"])
                i+=1
            
            avgTime = (sum(timeList)/iterations)*1000
            avgStates = sum(state_countList)/iterations
            print(f"""
Search depth {depth}:
  -       Best moves: {getBestMoves(bestMoves)}
  -    Average value: {sum(valueList)/iterations}
  -     Average time: {avgTime} ms
  - Generated states: {avgStates} states
  -    Average speed: {avgStates/(avgTime/1000)} state/s
                  """)
            depth += 1
        print("\n\n\n")
    print()

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

mst3([startGame,midGame,endGame],3, 10)

print(f"\nTest took {time() - start} seconds.\n")