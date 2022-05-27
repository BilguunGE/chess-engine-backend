from typing import ValuesView
import numpy as np
# moves -- 0 = blackPawns, 1 = whitePawns, 2 = Rooks, 3 = Bishops, 4 = Kings, 5 = Knights
def allMovesGen():
    moves = []
    x = 0
    movesH = []
    while x < 8:
        y = 0
        while y < 8:
            newMoves = np.array(0,dtype=np.uint64)
            possibleCatches = np.array(0,dtype=np.uint64)
            _newMoves_ = np.uint64(0)
            _possibleCatches_ = np.uint64(0)
            if x == 1:
                newMoves = np.append(newMoves, np.uint64(1 << ((x+2)*8+y)))
                _newMoves_ |= np.uint64(1 << ((x+2)*8+y))
            if y > 0 and x < 7:
                possibleCatches = np.append(possibleCatches, np.uint64(1 << ((x+1)*8+y-1)))
                _possibleCatches_ |= np.uint64(1 << ((x+1)*8+y-1))
            if y < 7 and x < 7:
                possibleCatches = np.append(possibleCatches, np.uint64(1 << ((x+1)*8+y+1)))
                _possibleCatches_ |= np.uint64(1 << ((x+1)*8+y+1))
            if x < 7:
                newMoves = np.append(newMoves, np.uint64(1 << ((x+1)*8+y)))
                _newMoves_ |= np.uint64(1 << ((x+1)*8+y))
            movesH.append((np.uint64(1 << (x*8+y)),(newMoves,possibleCatches),(_newMoves_, _possibleCatches_)))
            y += 1
        x += 1
    moves.append(movesH)
    x = 0
    movesH = []
    while x < 8:
        y = 0
        while y < 8:
            newMoves = np.array(0,dtype=np.uint64)
            possibleCatches = np.array(0,dtype=np.uint64)
            _newMoves_ = np.uint64(0)
            _possibleCatches_ = np.uint64(0)
            if y > 0 and x > 0:
                possibleCatches = np.append(possibleCatches, np.uint64(1 << ((x-1)*8+y-1)))
                _possibleCatches_ |= np.uint64(1 << ((x-1)*8+y-1))
            if y < 7 and x > 0:
                possibleCatches = np.append(possibleCatches, np.uint64(1 << ((x-1)*8+y+1)))
                _possibleCatches_ |= np.uint64(1 << ((x-1)*8+y+1))
            if x == 6:
                newMoves = np.append(newMoves, np.uint64(1 << ((x-2)*8+y)))
                _newMoves_ |= np.uint64(1 << ((x-2)*8+y))
            if x > 0:
                newMoves = np.append(newMoves, np.uint64(1 << ((x-1)*8+y)))
                _newMoves_ |= np.uint64(1 << ((x-1)*8+y))
            movesH.append((np.uint64(1 << (x*8+y)),(newMoves,possibleCatches),(_newMoves_, _possibleCatches_)))
            y += 1
        x += 1
    moves.append(movesH)
    x = 0
    movesH = []
    while x < 8:
        y = 0
        while y < 8:
            newMoves = np.array(0,dtype=np.uint64)
            _newMoves_ = np.uint64(0)
            x1 = (x + 1) % 8
            y1 = (y + 1) % 8
            while x1 != x:
                newMoves = np.append(newMoves, np.uint64(1 << ((x1)*8+y)))
                _newMoves_ |= np.uint64(1 << ((x1)*8+y))
                x1 = (x1 + 1) % 8
            while y1 != y:
                newMoves = np.append(newMoves, np.uint64(1 << ((x)*8+y1)))
                _newMoves_ |= np.uint64(1 << ((x)*8+y1))
                y1 = (y1 + 1) % 8
            movesH.append((np.uint64(1 << (x*8+y)),newMoves,_newMoves_))
            y += 1
        x += 1
    moves.append(movesH)
    movesH = []
    x = 0
    while x < 8:
        y = 0
        while y < 8:
            x1 = x
            y1 = y
            newMoves = np.array(0,dtype=np.uint64)
            _newMoves_ = np.uint64(0)
            while x1 < 7 and y1 < 7:
                x1 += 1
                y1 += 1
                newMoves = np.append(newMoves, np.uint64(1 << (x1*8 + y1)))
                _newMoves_ |= np.uint64(1 << (x1*8 + y1))
            x1 = x
            y1 = y
            while x1 < 7 and y1 > 0:
                x1 += 1
                y1 -= 1
                newMoves = np.append(newMoves, np.uint64(1 << (x1*8 + y1)))
                _newMoves_ |= np.uint64(1 << (x1*8 + y1))
            x1 = x
            y1 = y
            while x1 > 0 and y1 > 0:
                x1 -= 1
                y1 -= 1
                newMoves = np.append(newMoves, np.uint64(1 << (x1*8 + y1)))
                _newMoves_ |= np.uint64(1 << (x1*8 + y1))
            x1 = x
            y1 = y
            while x1 > 0 and y1 < 7:
                x1 -= 1
                y1 += 1
                newMoves = np.append(newMoves, np.uint64(1 << (x1*8 + y1)))
                _newMoves_ |= np.uint64(1 << (x1*8 + y1))
            movesH.append((np.uint64(1 << (x*8+y)),newMoves,_newMoves_))
            y += 1
        x += 1
    moves.append(movesH)
    movesH = []
    x = 0
    while x < 8:
        y = 0
        while y < 8:
            newMoves = np.array(0,dtype=np.uint64)
            _newMoves_ = np.uint64(0)
            if x > 0 and y > 0:
                newMoves = np.append(newMoves, np.uint64(1 << ((x-1)*8 + y-1)))
                _newMoves_ |= np.uint64(1 << ((x-1)*8 + y-1))
            if x < 7 and y > 0:
                newMoves = np.append(newMoves, np.uint64(1 << ((x+1)*8 + y-1)))
                _newMoves_ |= np.uint64(1 << ((x+1)*8 + y-1))
            if x < 7 and y < 7:
                newMoves = np.append(newMoves, np.uint64(1 << ((x+1)*8 + y+1)))
                _newMoves_ |= np.uint64(1 << ((x+1)*8 + y+1))
            if x > 0 and y < 7:
                newMoves = np.append(newMoves, np.uint64(1 << ((x-1)*8 + y+1)))
                _newMoves_ |= np.uint64(1 << ((x-1)*8 + y+1))
            if x > 0:
                newMoves = np.append(newMoves, np.uint64(1 << ((x-1)*8 + y)))
                _newMoves_ |= np.uint64(1 << ((x-1)*8 + y))
            if x < 7:
                newMoves = np.append(newMoves, np.uint64(1 << ((x+1)*8 + y)))
                _newMoves_ |= np.uint64(1 << ((x+1)*8 + y))
            if y < 7:
                newMoves = np.append(newMoves, np.uint64(1 << ((x)*8 + y+1)))
                _newMoves_ |= np.uint64(1 << ((x)*8 + y+1))
            if y > 0:
                newMoves = np.append(newMoves, np.uint64(1 << ((x)*8 + y-1)))
                _newMoves_ |= np.uint64(1 << ((x)*8 + y-1))
            movesH.append((np.uint64(1 << (x*8+y)),newMoves,_newMoves_))
            y += 1
        x += 1
    moves.append(movesH)
    movesH = []
    x = 0
    while x < 8:
        y = 0
        while y < 8:
            newMoves = np.array(0,dtype=np.uint64)
            _newMoves_ = np.uint64(0)
            if x > 0 and y > 1:
                newMoves = np.append(newMoves, np.uint64(1 << ((x-1)*8 + y-2)))
                _newMoves_ |= np.uint64(1 << ((x-1)*8 + y-2))
            if x > 0 and y < 6:
                newMoves = np.append(newMoves, np.uint64(1 << ((x-1)*8 + y+2)))
                _newMoves_ |= np.uint64(1 << ((x-1)*8 + y+2))
            if x > 1 and y < 7:
                newMoves = np.append(newMoves, np.uint64(1 << ((x-2)*8 + y+1)))
                _newMoves_ |= np.uint64(1 << ((x-2)*8 + y+1))
            if x > 1 and y > 0:
                newMoves = np.append(newMoves, np.uint64(1 << ((x-2)*8 + y-1)))
                _newMoves_ |= np.uint64(1 << ((x-2)*8 + y-1))
            if x < 7 and y > 1:
                newMoves = np.append(newMoves, np.uint64(1 << ((x+1)*8 + y-2)))
                _newMoves_ |= np.uint64(1 << ((x+1)*8 + y-2))
            if x < 7 and y < 6:
                newMoves = np.append(newMoves, np.uint64(1 << ((x+1)*8 + y+2)))
                _newMoves_ |= np.uint64(1 << ((x+1)*8 + y+2))
            if x < 6 and y > 0:
                newMoves = np.append(newMoves, np.uint64(1 << ((x+2)*8 + y-1)))
                _newMoves_ |= np.uint64(1 << ((x+2)*8 + y-1))
            if x < 6 and y < 7:
                newMoves = np.append(newMoves, np.uint64(1 << ((x+2)*8 + y+1)))
                _newMoves_ |= np.uint64(1 << ((x+2)*8 + y+1))
            movesH.append((np.uint64(1 << (x*8+y)),newMoves,_newMoves_))
            y += 1
        x += 1
    moves.append(movesH)
    return moves
# shadows -- 0 = rooks, 1 = bishops 
def allShadowsGen():
    shadows = []
    x = 0
    shadowsH = []
    while x < 8:
        y = 0
        while y < 8:
            newShadows = np.array([np.uint64(0)]*64)
            x1 = (x + 1) % 8
            y1 = (y + 1) % 8
            while x1 != x:
                x2 = x1
                _shadows_ = np.uint64(0)
                if x2 < x:
                    x2 -= 1
                    while x2 >= 0:
                        _shadows_ |= np.uint64(1 << ((x2)*8+y))
                        x2 -= 1
                if x2 > x:
                    x2 += 1
                    while x2 <= 7:
                        _shadows_ |= np.uint64(1 << ((x2)*8+y))
                        x2 += 1
                newShadows[(x1*8+y)] = _shadows_
                x1 = (x1 + 1) % 8
            while y1 != y:
                y2 = y1
                _shadows_ = np.uint64(0)
                if y2 < y:
                    y2 -= 1
                    while y2 >= 0:
                        _shadows_ |= np.uint64(1 << ((x)*8+y2))
                        y2 -= 1
                if y2 > y:
                    y2 += 1
                    while y2 <= 7:
                        _shadows_ |= np.uint64(1 << ((x)*8+y2))
                        y2 += 1
                newShadows[(x*8+y1)] = _shadows_
                y1 = (y1 + 1) % 8
            shadowsH.append(newShadows)
            y += 1
        x += 1
    shadows.append(shadowsH)
    shadowsH = []
    x = 0
    while x < 8:
        y = 0
        while y < 8:
            x1 = x
            y1 = y
            newShadows = np.array([np.uint64(0)]*64)
            while x1 < 7 and y1 < 7:
                _shadows_ = np.uint64(0)
                x1 += 1
                y1 += 1
                x2 = x1 + 1
                y2 = y1 + 1
                while x2 < 8 and y2 < 8: 
                    _shadows_ |= np.uint64(1 << (x2*8 + y2))
                    x2 += 1
                    y2 += 1
                newShadows[(x1*8+y1)] = _shadows_
            x1 = x
            y1 = y
            while x1 < 7 and y1 > 0:
                _shadows_ = np.uint64(0)
                x1 += 1
                y1 -= 1
                x2 = x1 + 1
                y2 = y1 - 1
                while x2 < 8 and y2 >= 0: 
                    _shadows_ |= np.uint64(1 << (x2*8 + y2))
                    x2 += 1
                    y2 -= 1
                newShadows[(x1*8+y1)] = _shadows_
            x1 = x
            y1 = y
            while x1 > 0 and y1 > 0:
                _shadows_ = np.uint64(0)
                x1 -= 1
                y1 -= 1
                x2 = x1 - 1
                y2 = y1 - 1
                while x2 >= 0 and y2 >= 0: 
                    _shadows_ |= np.uint64(1 << (x2*8 + y2))
                    x2 -= 1
                    y2 -= 1
                newShadows[(x1*8+y1)] = _shadows_
            x1 = x
            y1 = y
            while x1 > 0 and y1 < 7:
                _shadows_ = np.uint64(0)
                x1 -= 1
                y1 += 1
                x2 = x1 - 1
                y2 = y1 + 1
                while x2 >= 0 and y2 < 8: 
                    _shadows_ |= np.uint64(1 << (x2*8 + y2))
                    x2 -= 1
                    y2 += 1
                newShadows[(x1*8+y1)] = _shadows_
            shadowsH.append(newShadows)
            y += 1
        x += 1
    shadows.append(shadowsH)
    return shadows

def betweenGen():
    between = []
    x = 0
    while x < 8:
        y = 0
        while y < 8:
            bw = [0]*64
            x1 = 0
            while x1 < 8:
                y1 = 0
                while y1 < 8:
                    bwH = np.uint64(0)
                    if x1 == x:
                        y2 = y1
                        while y2 + 1 < y:
                            y2 += 1
                            bwH |= np.uint64(1 << (x*8 + y2))
                        while y + 1 < y2:
                            y2 -= 1
                            bwH |= np.uint64(1 << (x*8 + y2))
                    elif y1 == y:
                        x2 = x1
                        while x2 + 1 < x:
                            x2 += 1
                            bwH |= np.uint64(1 << (x2*8 + y))
                        while x + 1 < x2:
                            x2 -= 1
                            bwH |= np.uint64(1 << (x2*8 + y))
                    elif x - x1 == y - y1:
                        x2 = x1
                        y2 = y1
                        while y2 + 1 < y:
                            y2 += 1
                            x2 += 1
                            bwH |= np.uint64(1 << (x2*8 + y2))
                        while y + 1 < y2:
                            y2 -= 1
                            x2 -= 1
                            bwH |= np.uint64(1 << (x2*8 + y2))
                    elif x - x1 == y1 - y:
                        x2 = x1
                        y2 = y1
                        while y2 + 1 < y:
                            y2 += 1
                            x2 -= 1
                            bwH |= np.uint64(1 << (x2*8 + y2))
                        while y + 1 < y2:
                            y2 -= 1
                            x2 += 1
                            bwH |= np.uint64(1 << (x2*8 + y2))
                    bw[x1*8+y1] = bwH
                    y1 += 1
                x1 += 1
            between.append(bw)
            y += 1
        x += 1
    return between

## alle möglichen Züge unterteilt in [Figur][Feld,Züge] wobei die Züge in np.array gespeichert werden
allMoves = allMovesGen()
## die Schatten aller Feld1 X Feld2 Möglichkeiten unterteilt in [Figur][Feld1][Schatten nach Feld2] wobei die Schatten in uint Repräsentation vorliegen
allShadows = allShadowsGen()
## alle Felder zwischen Feld1 und Feld unterteilt in [Feld1][Felder zwischen Feld1 unf Feld2] wobei die Felder in uint Repräsentation vorliegen
between = betweenGen()