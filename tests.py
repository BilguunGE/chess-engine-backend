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
    moves = list(map(getMoveToString, board.getMoves()))
    move, score  = MCTS().findNextMove(board, time()+5, moves)
    print(move.get('toString'))

def mctsBenchmarkTest(board, iterations, boardName):
    expansions = 0
    for i in range(iterations):
        start = time()
        end = start + 1
        move, stats = MCTS().findNextMove(board, end)
        expansions+= stats.get('expansions')

    print(boardName)
    print('iterations: '+str(iterations))
    print('avg expansions: '+str(expansions/iterations)+'/s')

def mctsQualityTest(board, iterations, timeInSec):
    moves = {}
    for i in range(iterations):
        start = time()
        end = start + timeInSec
        move, stats = MCTS().findNextMove(board, end)
        if move['toString'] in moves:
            moves[move['toString']] +=1
        else:
            moves[move['toString']] =1
    print(moves)
    
def testHist(board):
    moves = board.getMoves()
    print(board.STATE_HISTORY)
    board.doMove(moves[0])
    print(board.STATE_HISTORY)
    board.undoLastMove()
    print(board.STATE_HISTORY)
    
def testFirstOnHillHist(board):
    
    i = 0
    while i < 3:
        board.doMove({'toString': 'Kb2a3', 'from': 49, 'to': 40, 'type': 'K', 'score': 0})
        board.doMove({'toString': 'Kg7f8', 'from': 14, 'to': 5, 'type': 'k', 'score': 0})
        board.doMove({'toString': 'Ka3b2', 'from': 40, 'to': 49, 'type': 'K', 'score': 0})
        board.doMove({'toString': 'Kf8g7', 'from': 5, 'to': 14, 'type': 'k', 'score': 0})
        print(board.STATE_HISTORY)
        print(board.is3Fold())
        i += 1
    board.undoAllMoves()
    print(board.STATE_HISTORY)
    print(board.is3Fold())
    
    
    
    
    
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
                value = alphaBeta(board, depth, -10000, 10000, 1, 1, time()*1000+120000,0,stateCount )
                # value = alphaBetaNoHash(board, depth, -10000, 10000, 1, 1, stateCount)
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
firstOnTheHill  = Board('7k/p6p/1p6/8/8/B7/B7/7K w - - 0 1')

# //////////////////////////////////////////////////////
#
#                    Tests
#
# //////////////////////////////////////////////////////

start = time()
mctsQualityTest(firstOnTheHill, 20, 20)
print(f"\nTest took {time() - start} seconds.\n")