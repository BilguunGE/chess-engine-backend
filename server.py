
from flask import Flask
from flask import request
from route import getMoves

app = Flask(__name__)


@app.route('/moves', methods=['GET','POST'])
def Moves():
    FEN = request.json['FEN']
    return getMoves(FEN)