from flask import Flask, request
from flask_cors import CORS
from route import getMoves

app = Flask(__name__)
CORS(app)


@app.route('/moves', methods=['GET','POST'])
def Moves():
    FEN = request.json['FEN']
    return getMoves(FEN)