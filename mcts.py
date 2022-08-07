import math
from random import randint
from time import time
from Board import Board

class State:
    board:Board
    visitCount:int = 0
    winScore:int = 0
    move:any
    isRoot = False
    
    def getAllPossibleStates(self, filterMoves:list = None):
        states = []
        if self.isRoot and filterMoves:
            allMoves = self.board.getMoves()
            moves = filter(lambda x: x['toString'] in filterMoves, allMoves)
        else:    
            moves = self.board.getMoves()
        for move in moves:
            self.board.doMove(move)
            state = State()
            state.board = Board(self.board.getFEN())
            state.move = move
            states.append(state)
            self.board.undoLastMove()
        return states

    def randomPlay(self):
        moves = self.board.getMoves()
        index = randint(0, len(moves) - 1)
        self.board.doMove(moves[index])

    def incrementVisit(self):
        self.visitCount+=1

    def addScore(self, value):
        self.winScore+=value

class Node:
    state:State
    children:list
    player:bool
    parent = None

    def __init__(self, state, children = []) -> None:
        self.state = state
        self.children = children

    def getRandomChildNode(self):
        index = randint(0, len(self.children)-1)
        return self.children[index]

    def getChildWithMaxScore(self):
        return max(self.children, key=lambda x: x.state.winScore)

class Tree:
    node:Node
    def __init__(self) -> None:
        self.node = Node(State())

class MCTS:
    WIN_SCORE = 10
    UCT_CONSTANT = 1.41
    OPPONENT:bool

    def findNextMove(self, board:Board, endTime, filterMoves:list = None):
        tree = Tree()
        self.OPPONENT = not board.isWhiteTurn
        rootNode = tree.node
        rootNode.player = board.isWhiteTurn
        rootNode.state.board = board
        rootNode.state.isRoot = True
        expansions = 0

        while time() < endTime:
            promisingNode = self.selectPromisingNode(rootNode)
            if promisingNode.state.board.isGameDone() == 0: 
                if promisingNode.state.isRoot and filterMoves:
                    self.expandNode(promisingNode, filterMoves)
                else:
                    self.expandNode(promisingNode)
            
            nodeToExplore = promisingNode
            if len(promisingNode.children) > 0 :
                nodeToExplore = promisingNode.getRandomChildNode()
            
            playoutResult = self.simulateRandomPlayout(nodeToExplore)
            self.backPropogation(nodeToExplore, playoutResult)

        winnerNode:Node = rootNode.getChildWithMaxScore()
        stats = {"winScore":winnerNode.state.winScore, "expansions":rootNode.state.visitCount}
        rootNode.children.clear()
        tree.node = winnerNode
        return (winnerNode.state.move, stats)


    ## SELECTION
    def selectPromisingNode(self, node:Node):
        while len(node.children) > 0: 
            node = self.findBestNodeWithUCT(node)
        return node

    ## EXPANSION
    def expandNode(self, node:Node, filterMoves:list = None):
        possibleStates:list[State] = node.state.getAllPossibleStates(filterMoves)
        for state in possibleStates:
            newNode = Node(state)
            newNode.parent = node
            newNode.player = not node.player
            newNode.children = []
            node.children.append(newNode)
    
    ## SIMULATION
    def simulateRandomPlayout(self, tempNode:Node):
        tempState = tempNode.state
        board = tempState.board

        if (board.didOpponentWin(self.OPPONENT)):
            tempNode.parent.state.winScore = float('-inf')
            return self.OPPONENT
        
        while board.isGameDone() == 0:
            tempState.randomPlay()

        winner = not tempState.board.isWhiteTurn
        tempState.board.undoAllMoves()
        
        return winner

    ## BACKPROPAGATION
    def backPropogation(self, nodeToExplore:Node, player):
        while True: 
            nodeToExplore.state.incrementVisit()
            if (nodeToExplore.player == player):
                nodeToExplore.state.addScore(self.WIN_SCORE)

            if nodeToExplore.parent is not None:
                nodeToExplore = nodeToExplore.parent
            else:
                break

    ## UCT
    def uctValue(self, totalVisit, nodeWinScore, nodeVisit, ):
        if nodeVisit == 0: 
            return float('inf')
        return (nodeWinScore /nodeVisit) + self.UCT_CONSTANT * math.sqrt(math.log(totalVisit) /nodeVisit)
    

    def findBestNodeWithUCT(self,  node:Node):
        parentVisit = node.state.visitCount
        return max(node.children,key=lambda x: self.uctValue(parentVisit, x.state.winScore, x.state.visitCount) )
    