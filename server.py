from flask import Flask, request
from flask_cors import CORS, cross_origin
import route

app = Flask(__name__)
CORS(app)
app.config['CORS_HEADERS'] = 'Content-Type'
state = route.GameState()

@app.route('/initBoard', methods=['POST'])
@cross_origin()
def initBoard():
    FEN = request.json['FEN']
    return state.initBoard(FEN)

@app.route('/getMoves', methods=['GET'])
@cross_origin()
def getMoves():
    return state.getMoves()

@app.route('/alphabeta', methods=['POST'])
@cross_origin()
def alphabeta():
    DEPTH = int(request.json['depth'])
    STOPTIME = int(request.json['stopTime'])
    return state.alphaBetaMove(DEPTH, STOPTIME)

@app.route('/mcts', methods=['POST'])
@cross_origin()
def mcts():
    MOVES = request.json['moves']
    STOPTIME = int(request.json['stopTime'])
    return state.mctsMove(MOVES, STOPTIME) 

@app.route('/doMove', methods=['POST'])
@cross_origin()
def doMove():
    print("executing move")
    MOVE = request.json['move']
    return state.doMove(MOVE)

@app.route('/undoLastMove', methods=['GET'])
@cross_origin()
def undoLastMove():
    print("Undoing last move")
    return state.undoLastMove()
