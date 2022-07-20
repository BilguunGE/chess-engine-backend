import chess
import chess.pgn
from io import StringIO
import regex as re
import sqlite3
import numpy as np
import bitarray

board = chess.Board()
l = []
pgn = open("test/lichess_db_kingOfTheHill_rated_2022-03.pgn")
data = []

def evals(line):
    pgn_list = []
    x = line.split(" ")
    y = 0 
    marker = False
    for i in x:
        if marker:
            pgn_list.append([i[:-1]])
            y += 1
            marker = False
        else:
            if i.startswith("[%eval"):
                marker = True
    return pgn_list

def bits(n):
    return [int(x) for x in bin(n)[2:].zfill(4)]

def fenToArray(fen):
    board = chess.Board(fen)
    binary = bitarray.bitarray()
    binary.extend(np.asarray(board.pieces(chess.PAWN, chess.WHITE).tolist()).astype(int))
    binary.extend(np.asarray(board.pieces(chess.PAWN, chess.BLACK).tolist()).astype(int))
    binary.extend(np.asarray(board.pieces(chess.KNIGHT, chess.WHITE).tolist()).astype(int))
    binary.extend(np.asarray(board.pieces(chess.KNIGHT, chess.BLACK).tolist()).astype(int))
    binary.extend(np.asarray(board.pieces(chess.BISHOP, chess.WHITE).tolist()).astype(int))
    binary.extend(np.asarray(board.pieces(chess.BISHOP, chess.BLACK).tolist()).astype(int))
    binary.extend(np.asarray(board.pieces(chess.ROOK, chess.WHITE).tolist()).astype(int))
    binary.extend(np.asarray(board.pieces(chess.ROOK, chess.BLACK).tolist()).astype(int))
    binary.extend(np.asarray(board.pieces(chess.QUEEN, chess.WHITE).tolist()).astype(int))
    binary.extend(np.asarray(board.pieces(chess.QUEEN, chess.BLACK).tolist()).astype(int))
    binary.extend(np.asarray(board.pieces(chess.KING, chess.WHITE).tolist()).astype(int))
    binary.extend(np.asarray(board.pieces(chess.KING, chess.BLACK).tolist()).astype(int))
    binary.extend([int(board.turn)])
    binary.extend([bool(board.castling_rights & chess.BB_A1), bool(board.castling_rights & chess.BB_H1), bool(board.castling_rights & chess.BB_A8), bool(board.castling_rights & chess.BB_H8)])
    en_passant = [0]*64
    if board.ep_square:
        en_passant[board.ep_square] = 1
    binary.extend(en_passant[16:23])
    binary.extend(en_passant[40:47])
    binary.extend(bin(board.halfmove_clock)[2:].zfill(8))
    binary.extend(bin(board.fullmove_number)[2:].zfill(8))
    return binary

while True:
    evals2 = []
    line = pgn.readline()
    if not line:
        break
    if re.match("1\. [a-zA-Z]+\d \{ \[%e", line):
        evals2 = evals(line)
        pgns = StringIO(line)
        game = chess.pgn.read_game(pgns)
        length = len(evals2)
        for number, move in enumerate(game.mainline_moves()):
            board.push(move)
            if number == length:
                break
            evals2[number].append(board.fen())
        data.extend(evals2)
        board.reset()

data2 = []
for x in data:
    if not str(x[0]).startswith("#"):
        data2.append([fenToArray(x[1]), x[0]])

blob = data2
Con = sqlite3.connect('koth_training.db')
Cur = Con.cursor()
#Cur.execute("create table training_data (id INTEGER PRIMARY KEY, binary BLOB , evals FLOAT)")
for x in data2:
    Cur.execute("insert into training_data (binary, evals) values (?,?)", (x[0], x[1]))
Con.commit()