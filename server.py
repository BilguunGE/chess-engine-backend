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


@app.route('/doMove', methods=['POST'])
@cross_origin()
def doMove():
    move = request.json['move']
    return route.doMove(move)

