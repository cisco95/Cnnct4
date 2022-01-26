import numpy as np
import random
import math

ROW_MAX = 6
COL_MAX = 7


def makeBoard(value=0):
    board = [[value for i in range(COL_MAX)] for j in range(ROW_MAX)]
    board = np.array(board)
    return board


def makeMove(board, ROW, COL, player):
    board[ROW][COL] = player


def checkMove(board, COL):
    if board[ROW_MAX-1][COL] == 0:
        isValid = True
    else:
        isValid = False

    return isValid


def getRow(board, COL):
    for i in range(ROW_MAX):
        if board[i][COL] == 0:
            return i


def openCols(board):
    openCol = []
    for x in range(COL_MAX):
        if checkMove(board, x):
            openCol.append(x)

    return openCol


def printBoard(board):
    print(np.flip(board, 0))

# -------------------------Start of AI section ------------------------------------


def evalOptions(window, player):
    score = 0
    if player == 1:
        opponent = -1
    else:
        opponent = 1

    # if window.count(player) == 4:
    #     score += 100
    # elif window.count(player) == 3 and window.count(0) == 1:
    #     score += 50
    # elif window.count(player) == 2 and window.count(0) == 2:
    #     score += 25
    # elif window.count(player) == 1 and window.count(0) == 3:
    #     score += 15

    # if window.count(opponent) == 3 and window.count(0) == 1:
    #     score -= 75
    # if window.count(opponent) == 2 and window.count(0) == 2:
    #     score -= 10

    if window.count(player) == 4:
        score += 100
    elif window.count(player) == 3 and window.count(0) == 1:
        score += 5
    elif window.count(player) == 2 and window.count(0) == 2:
        score += 2

    if window.count(opponent) == 3 and window.count(0) == 1:
        score -= 4

    if window.count(opponent) == 2 and window.count(0) == 2:
        score -= 1

    return score


def scoreLocation(board, player):
    score = 0

    # horizontal
    for i in range(ROW_MAX):
        rowArr = [int(x) for x in list(board[i, :])]
        for j in range(COL_MAX - 3):
            window = rowArr[j:j+4]

            score += evalOptions(window, player)

    # vertical
    for j in range(COL_MAX):
        colArr = [int(x) for x in list(board[:, j])]
        for i in range(ROW_MAX - 3):
            window = colArr[i:i+4]

            score += evalOptions(window, player)

    # diagonal 1/1
    for i in range(ROW_MAX - 3):
        for j in range(COL_MAX - 3):
            window = [board[i+x][j+x] for x in range(4)]

            score += evalOptions(window, player)

    # diagonal -1/1
    for i in range(ROW_MAX - 3):
        for j in range(COL_MAX - 3):
            window = [board[i+3-x][j+x] for x in range(4)]

            score += evalOptions(window, player)

    # center preference
    centerArr = [int(x) for x in list(board[:, 3])]
    centerAmount = centerArr.count(player)
    score += centerAmount * 4

    return score


def bestMove(board, player):
    bestScore = -10000
    possibleMoves = openCols(board)
    bestScoreLocation = random.choice(possibleMoves)
    for i in possibleMoves:
        row = getRow(board, i)
        temp_board = board.copy()
        makeMove(temp_board, row, i, player)
        score = scoreLocation(temp_board, player)
        if (score > bestScore):
            bestScore = score
            bestScoreLocation = i
    return bestScoreLocation


# ------------------------- END of AI section  ------------------------------------

def checkForWin(board, player):
    # vertical win:
    for j in range(COL_MAX):
        for i in range(ROW_MAX - 3):
            if board[i][j] == board[i+1][j] == board[i+2][j] == board[i+3][j] == player:
                return True

    # horizontal win:
    for j in range(COL_MAX - 3):
        for i in range(ROW_MAX):
            if board[i][j] == board[i][j+1] == board[i][j+2] == board[i][j+3] == player:
                return True

    # Diagonal(forward-up) win:
    for j in range(COL_MAX - 3):
        for i in range(ROW_MAX - 3):
            if board[i][j] == board[i+1][j+1] == board[i+2][j+2] == board[i+3][j+3] == player:
                return True

    # Diagonal(backward-up) win:
    for j in range(COL_MAX - 3):
        for i in range(3, ROW_MAX):
            if board[i][j] == board[i-1][j+1] == board[i-2][j+2] == board[i-3][j+3] == player:
                return True


def checkTerminalBoard(board):
    return checkForWin(board, -1) or checkForWin(board, 1) or len(openCols(board)) == 0

# --------------------------------------------------------------------------------------------------------------------------
# -------------------------- minimax pseudocode ------------------------------
# function minimax(node, depth, maximizingPlayer) is
#     if depth = 0 or node is a terminal node then
#         return the heuristic value of node
#     if maximizingPlayer then
#         value := −∞
#         for each child of node do
#             value := max(value, minimax(child, depth − 1, FALSE))
#         return value
#     else (* minimizing player *)
#         value := +∞
#         for each child of node do
#             value := min(value, minimax(child, depth − 1, TRUE))
#         return value
# -------------------------- minimax pseudocode ------------------------------


def minimax(board, depth, alpha, beta, maxPlayer):
    validMoves = openCols(board)
    terminal = checkTerminalBoard(board)

    if depth == 0 or terminal:
        if terminal:
            if checkForWin(board, -1):
                return (None, 1000000000)
            elif checkForWin(board, 1):
                return (None, -1000000000)
            else:
                return (None, 0)
        else:
            return (None, scoreLocation(board, -1))
    if maxPlayer:
        value = -math.inf
        column = random.choice(validMoves)
        for col in validMoves:
            row = getRow(board, col)
            board_copy = board.copy()
            makeMove(board_copy, row, col, -1)
            new_score = minimax(board_copy, depth - 1, alpha, beta, False)[1]
            if new_score > value:
                value = new_score
                column = col
            alpha = max(alpha, value)
            if alpha >= beta:
                break
        return column, value

    else:
        value = math.inf
        column = random.choice(validMoves)
        for col in validMoves:
            row = getRow(board, col)
            board_copy = board.copy()
            makeMove(board_copy, row, col, 1)
            new_score = minimax(board_copy, depth - 1, alpha, beta, True)[1]
            if new_score < value:
                value = new_score
                column = col
            beta = min(beta, value)
            if alpha >= beta:
                break

        return column, value


'''
# incrementing numbers board to test printBoard function

board = makeBoard()
number = 0
for i in range(ROW_MAX):
    for j in range(COL_MAX):
        board[i][j] = number
        number += 1
'''


# board = makeBoard()

'''
# played game board to test checkForWin function (checks all possibilities)
# horizontal win
board[0][1] = board[0][2] = board[0][4] = board[0][6] = board[1][1] = board[1][3] = board[1][4] = -1
board[0][3] = board[1][2] = board[2][1] = board[2][2] = board[2][3] = board[2][4] = board[3][4] = 1
# vertical win
board[0][0] = board[0][2] = board[0][4] = board[1][1] = board[2][0] = board[2][2] = board[3][0] = -1
board[0][1] = board[0][3] = board[1][0] = board[1][2] = board[1][3] = board[2][1] = board[2][3] = board[3][3] = 1
# Forward-up win
board[2][1] = board[0][2] = board[0][4] = board[0][6] = board[1][1] = board[1][3] = board[1][4] = -1
board[0][1] = board[0][3] = board[1][2] = board[2][2] = board[2][3] = board[2][4] = board[3][4] = 1
# Backward-up win
board[0][0] = board[0][2] = board[0][4] = board[1][1] = board[2][0] = board[2][2] = board[2][3] = -1
board[0][1] = board[0][3] = board[1][0] = board[1][2] = board[1][3] = board[2][1] = board[3][0] = board[3][3] = 1
'''

# printBoard(board)


# print(checkForWin(board, 1))
