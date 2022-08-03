from time import time
from Board import *
from helpers import *
from minimax import *
import json
from mcts import MCTS

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
    
def testEvaluationSpeed(board, iterations):
    i = 0 
    list =[]
    while i < iterations:
        start = time()
        board.evaluate()
        list.append(time()-start)
        i+=1
    print(sum(list)/1000)
    
def testNNEvaluationSpeed(board, iterations):
    i = 0 
    list =[]
    while i < iterations:
        start = time()
        board.evaluateNN()
        list.append(time()-start)
        i+=1
    print(sum(list)/1000)
    
    
def testAlphaBeta(board, depth, stopTime, iterations):
    i = 0
    list = []
    while i< iterations:
        start = time()
        alphaBeta(board,depth,-10000,10000,1,1,stopTime, 0)
        list.append(time()-start)
        i += 1
    print(str((sum(list)*1000)/len(list))+"ms")
    
def testAlphaBetaNN(board, depth, stopTime, iterations):
    i = 0
    list = []
    while i< iterations:
        start = time()
        alphaBeta(board,depth,-10000,10000,1,1,stopTime, 1)
        list.append(time()-start)
        i += 1
    print(str((sum(list)*1000)/len(list))+"ms")
    
def testAlphaBetaNewTT(fen, depth, stopTime, iterations):
    i = 0
    list = []
    while i< iterations:
        board = Board(fen)
        start = time()
        alphaBeta(board,depth,-10000,10000,1,1,stopTime, 0)
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
    print("castleRight: ", board.stringifyCastleRights())
    print("enPassant: ", board.enPassant)
    print("half: ", board.halfmoveClock)
    print("full: ", board.fullmoveCount)

def simpleTest():
    with open('test.json') as testFile:
        tests = json.load(testFile)
        result = []
        for fen in tests:
            movesLen = len(Board(fen).getMoves())
            result.append((fen, movesLen == tests[fen].get("n_legal_moves")))
        filteredResult =  list(filter(lambda x: not x[1], result))
        if filteredResult:
            print(filteredResult)
        else:
            print('All right')

def moveTest():
    with open('test.json') as testFile:
        tests = json.load(testFile)
        for fen in tests:
            subsequent_boards = tests[fen]['subsequent_boards']
            board = Board(fen)
            moves = board.getMoves()
            for move in moves:
                board.doMove(move)
                newFEN = board.getFEN()
                board.undoLastMove()
                if not newFEN in subsequent_boards:
                    print(fen, move, newFEN)
                    return (newFEN, move)
    print('All right')
    
def mctsTest(board):
    move, score  = MCTS().findNextMove(board, time()+5, list(map(getMoveToString, board.getMoves())))
    print(move.get('toString'))
    
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
                board.best_moves.clear()
                start = time()
                # value = alphaBeta(board, depth, -10000, 10000, 1, 1, time()*1000+120000,0,stateCount )
                value = alphaBetaNoHash(board, depth, -10000, 10000, 1, 1, stateCount)
                timeList.append(time()-start)
                valueList.append(value)
                state_countList.append(stateCount["count"])
                i+=1
            
            avgTime = (sum(timeList)/iterations)*1000
            avgStates = sum(state_countList)/iterations
            print(f"""
Search depth {depth}:
  -       Best moves: {board.best_moves}
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
finalMoveGame = Board("6Bk/Q7/8/8/8/3K4/8/8 w - - 0 1")
firstOnTheHill  = Board('8/6k1/8/8/8/8/1K6/8 w - - 0 1')

# //////////////////////////////////////////////////////
#
#                    Tests
#
# //////////////////////////////////////////////////////

start = time()

mctsTest(finalMoveGame)

print(f"\nTest took {time() - start} seconds.\n")