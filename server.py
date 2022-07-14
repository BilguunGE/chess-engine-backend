from flask import Flask, request
from flask_cors import CORS, cross_origin
import route

app = Flask(__name__)
CORS(app)
app.config['CORS_HEADERS'] = 'Content-Type'


@app.route('/initBoard', methods=['POST'])
@cross_origin()
def initBoard():
    FEN = request.json['FEN']
    return route.initBoard(FEN)

@app.route('/getMoves', methods=['GET'])
@cross_origin()
def getMoves():
    return route.getMoves()

@app.route('/alphabeta', methods=['POST'])
@cross_origin()
def alphabeta():
    print("received request")
    DEPTH = int(request.json['depth'])
    ALPHA = int(request.json['alpha'])
    BETA = int(request.json['beta'])
    STOPTIME = int(request.json['stopTime'])
    return route.alphaBetaMove(DEPTH, ALPHA, BETA, STOPTIME)
