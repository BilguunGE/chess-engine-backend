from operator import itemgetter
from random import randint, random
from time import time
import numpy as np

def trailingZeros(v):
     return (v & -v).bit_length() - 1

def strBBtoBB(str):
    bbStr = str.replace("\n","").replace(" ","")
    return int(bbStr,2)
    
def printBits(num, title=''):
    print()
    print(title)
    print()
    print(insert_newlines('{:064b}'.format(num), 8))
    print()

def insert_newlines(string, every=64):
    lines = []
    for i in range(0, len(string), every):
        newLine = string[i:i+every]
        lines.append(newLine[::-1])
    lines.reverse()
    return '\n'.join(lines)

def reverse(s):
    s = np.binary_repr(s,width=64)
    return np.uint64(int(s[::-1], 2))
    
def makeField(row, col):
    colNames = ["a", "b", "c", "d", "e", "f", "g", "h"]
    rowNames = ["8", "7", "6", "5", "4", "3", "2", "1"]
    return colNames[col] + rowNames[row]

def castleStrToArr(str):
    result = [False,False,False,False]
    for s in str:
        if s == "K":
            result[0] = True
        if s == "Q":
            result[1] = True
        if s == "k":
            result[2] = True
        if s == "q":
            result[3] = True
    return result

def printTTable(board):
    result = ""
    for k in board.ttable:
        result += f"{k} {board.ttable[k]}\n"
    print(result)

def printMoves(moves):
    result = ""
    for move in moves:
        result += move["toString"] + "\n"
    print(result)
    print(len(moves))
    
def printBestMoves(moves):
    result = ""
    for move in moves:
        result += str(move["move"]["toString"]) + " " + str(move["value"]) + "\n"
    print(result)
    
def getBoardStr(board):
    list = board.convertBitboardsToArray()
    result = ""
    for row in list:
        for cell in row:
            if cell == "":
                result+= ". "
            else:
                result += cell + " "
        result+='\n'
    return result

def countSetBits(number):
    return bin(number).count('1') 

def pickRandom(list):
    randIndex = randint(0, len(list)-1)
    return list[randIndex]

def getBestMoves(list, key='value'):
    if len(list)==0:
        print("Can't pick best element. Empty list!")
        return
    highestVal = max(list, key=itemgetter(key))[key]
    moves = []
    for move in list:
        if move["value"] == highestVal:
            moves.append(move["move"]["toString"])
    return moves

def pickRandomBest(list, key='value'):
    if len(list)==0:
        print("Can't pick best element. Empty list!")
        return
    highestVal = max(list, key=itemgetter(key))[key]
    moves = []
    for move in list:
        if move["value"] == highestVal:
            moves.append(move)
    return pickRandom(moves)

def getMoveToString(move):
    return move["toString"]

def isTimeUp(stopTime):
    return time() * 1000 - 500 >= stopTime