import numpy as np
import json


# converts np board (np 2d array) into json list.
def exportBoard(board):
    jsonBoard = json.dumps(board.tolist())
    return jsonBoard


# converts json list into np board (np 2d array)
def importBoard(jsonBoard):
    board = np.array(json.loads(jsonBoard))
    return board
