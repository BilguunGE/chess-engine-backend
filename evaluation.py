from Board import *
from utils import *
import numpy as np

def evaluate(board):
    color = board.white
    enemy = board.black
    if not board.isWhite:
        color = board.black
        enemy = board.white
    pawnDelta = nonzeroElements(board.pawn & color).size - nonzeroElements(board.pawn & enemy).size
    bishopDelta = nonzeroElements(board.bishop & color).size - nonzeroElements(board.bishop & enemy).size
    knightDelta = nonzeroElements(board.knight & color).size - nonzeroElements(board.knight & enemy).size
    rookDelta = nonzeroElements(board.rook & color).size - nonzeroElements(board.rook & enemy).size
    queenDelta = nonzeroElements(board.queen & color).size - nonzeroElements(board.queen & enemy).size
    check = inCheck(board, enemy, color, not board.isWhite) - inCheck(board, color, enemy, board.isWhite)

    # TODO 1: include  checkmate (very high value), king of the hill (very high value), remis (negative value)

    # TODO 2: implement multiple evaluation functions => z.B. Ruhesuche bei vielen Figuren
    
    return 10 * check + 9 * queenDelta + 5 * rookDelta + 3 * knightDelta + 3 * bishopDelta + 1 * pawnDelta