from flask import Flask, request
from flask_cors import CORS, cross_origin
from route import getMoves

app = Flask(__name__)
CORS(app)
app.config['CORS_HEADERS'] = 'Content-Type'



@app.route('/moves', methods=['GET','POST'])
@cross_origin()
def Moves():
    FEN = request.json['FEN']
    return getMoves(FEN)