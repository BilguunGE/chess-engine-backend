import math
from random import randint
from time import time
from Board import Board

ttable = {}
class State:
    board:Board
    visitCount:int = 0
    winScore:int = 0
    move:any
    
    def getAllPossibleStates(self):
        states = []
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
        ttable[self.board.hash] = {"winScore" : self.winScore, "visits":self.visitCount}

    def addScore(self, value):
        self.winScore+=value
        ttable[self.board.hash] = {"winScore" : self.winScore, "visits":self.visitCount}

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
        child = self.children[index]
        if ttable.get(self.state.board.hash):
            tentry = ttable.get(self.state.board.hash)
            child.state.visitCount = tentry.get('visits') or 0
            child.state.winScore = tentry.get('winScore') or 0
        return child

    def getChildWithMaxScore(self, movesList = None):
        if not movesList is None:
            filteredChildren = filter(lambda elem: elem.state.move.get('toString') in movesList, self.children)
            return max(filteredChildren, key=lambda x: x.state.winScore)
        else:
            return max(self.children, key=lambda x: x.state.winScore)

class Tree:
    node:Node
    def __init__(self) -> None:
        self.node = Node(State())

class MCTS:
    WIN_SCORE = 10
    UTC_CONSTANT = 1.41 # we need proper value
    OPPONENT:bool

    def findNextMove(self, board:Board, endTime):
        tree = Tree()
        self.OPPONENT = not board.isWhiteTurn
        rootNode = tree.node
        rootNode.player = board.isWhiteTurn
        rootNode.state.board = board

        while time() < endTime:
            promisingNode = self.selectPromisingNode(rootNode)
            if not promisingNode.state.board.isGameDone(): 
                self.expandNode(promisingNode)
            
            nodeToExplore = promisingNode
            if len(promisingNode.children) > 0 :
                nodeToExplore = promisingNode.getRandomChildNode()
            
            playoutResult = self.simulateRandomPlayout(nodeToExplore)
            self.backPropogation(nodeToExplore, playoutResult)

        winnerNode:Node = rootNode.getChildWithMaxScore()
        tree.node = winnerNode
        return (winnerNode.state.move, winnerNode.state.winScore)


    ## SELECTION
    def selectPromisingNode(self, node:Node):
        while len(node.children) > 0: 
            node = self.findBestNodeWithUCT(node)
        return node

    ## EXPANSION
    def expandNode(self, node:Node):
        possibleStates:list[State] = node.state.getAllPossibleStates()
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
        
        while not board.isGameDone():
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

    ## UTC
    def uctValue(self, totalVisit, nodeWinScore, nodeVisit, ):
        if nodeVisit == 0: 
            return float('inf')
        return (nodeWinScore /nodeVisit) + self.UTC_CONSTANT * math.sqrt(math.log(totalVisit) /nodeVisit)
    

    def findBestNodeWithUCT(self,  node:Node):
        parentVisit = node.state.visitCount
        return max(node.children,key=lambda x: self.uctValue(parentVisit, x.state.winScore, x.state.visitCount) )
    




