import tweepy
import time
import dbCnnct4 as db
import dbBoard
import connect4
import os
import random
import string
import math
import re
import numpy as np

# import keys from auth, keys generated from twitter developer console. 
from auth import (
    consumer_key, # "API Key"
    consumer_secret, # "API Key Secret"
    access_token, 
    access_token_secret
)
# from twitter_cnnct4 import make_board_string, print_twitter_board

auth = tweepy.OAuth1UserHandler(consumer_key, consumer_secret, access_token, access_token_secret)

api = tweepy.API(auth, wait_on_rate_limit=True)
client = tweepy.Client(auth, wait_on_rate_limit=True)


def print_twitter_board(board):
    COL_MAX = 7
    ROW_MAX = 6
    newBoard = [['' for i in range(COL_MAX)] for j in range(ROW_MAX)]
    for i in range(COL_MAX):
        for j in range(ROW_MAX):
            if board[j][i] == 0:
                newBoard[j][i] = '⚪️'
            elif board[j][i] == 1:
                newBoard[j][i] = '🔴'
            elif board[j][i] == -1:
                newBoard[j][i] = '🟡'
            else:
                print("Error!")

    newBoard = np.array(newBoard)
    return newBoard


def make_board_string(board):
    COL_MAX = 7
    ROW_MAX = 6
    printable_board = ''

    for i in range(ROW_MAX):
        temp_string = ''
        for j in range(COL_MAX):
            temp_string += str(board[i][j])

        temp_string += '\n'
        printable_board = temp_string + printable_board
        # append_string(printable_board, temp_string)
    return printable_board


def get_screen_name(id):
    user = api.get_user(id)
    screen_name = user.screen_name
    return screen_name


def get_new_mentions():
    f = open('latest_mention_id.txt', 'r')
    sinceID = f.readline()
    f.close()
    mentionList = []

    maxID = str(api.mentions_timeline()[0].id)

    if maxID == sinceID:
        print("~~~~~~~~~~~~No new mentions~~~~~~~~~~~~")
        return
    else:
        while True:
            tweets = api.mentions_timeline(since_id=sinceID, max_id=maxID)
            if not tweets:
                break
            elif tweets[-1].id == maxID:
                break
            else:
                if not mentionList:
                    mentionList.extend(tweets)

                else:
                    tweets.pop(0)
                    if not tweets:
                        break
                    mentionList.extend(tweets)
                    print("~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~")
                maxID = str(tweets[-1].id)

# Uncomment below to test all mentions.

        sinceID = str(api.mentions_timeline()[0].id)
        f = open('latest_mention_id.txt', 'w+')
        f.write(f'{sinceID}')
        f.close()

        for tweet in mentionList:
            print(tweet.text)

        return mentionList


def cnnct4():
    keywords = {"scoreboard", "new game", "board", "surrender"}
    while True:

        tweets = get_new_mentions()
        reply = ""
        if tweets:
            for tweet in tweets:
                uid = tweet.user.id_str
                screenName = tweet.user.screen_name
                tweetID = tweet.id
                userResponse = tweet.text.lower()
                userResponse = userResponse.replace('@letscnnct4 ', '')
                try:
                    userResponse = int(userResponse)
                except:
                    pass
                print("Response:", userResponse)
                if type(userResponse) == int and (userResponse in range(1, 8)):
                    # user likely has made a move... check DB to see if they are a new player or continuing an active game.
                    dbItem = db.queryItem(uid)
                    board = connect4.makeBoard()
                    if dbItem['gameStatus'] == 'new':
                        reply = "Welcome to Connect4! "
                    elif dbItem['gameStatus'] == 'inactive':
                        reply = "Coming back for more Connect4? Lets go! "
                    else:
                        board = dbBoard.importBoard(dbItem['gameBoard'])
                    COL = int(userResponse)
                    COL -= 1
                    connect4.makeMove(
                        board, connect4.getRow(board, COL), COL, 1)
                    if connect4.checkForWin(board, 1):
                        print_B = str(make_board_string(
                            print_twitter_board(board)))
                        my_reply = api.update_status(
                            status=f'@{screenName} WOW! You are an expert! Congrats on beating me!\n{print_B}', in_reply_to_status_id=tweetID)
                        db.updateUser(uid, 'inactive', board)
                        db.userWin(uid)
                    else:
                        # make move, update db, reply to player.
                        columnChoice, minimax_score = connect4.minimax(
                            board, 6, -math.inf, math.inf, True)
                        connect4.makeMove(board, connect4.getRow(
                            board, columnChoice), columnChoice, -1)
                        print_B = make_board_string(print_twitter_board(board))
                        if connect4.checkForWin(board, -1):
                            my_reply = api.update_status(
                                status=f'@{screenName} Oops! Sorry, I beat you! Try again sometime!\n{print_B}', in_reply_to_status_id=tweetID)
                            db.updateUser(uid, 'inactive', board)
                            db.userLose(uid)

                        else:
                            stat = reply + "Here is the current board! Remember to check our pinned tweet to see how to play!\n" + print_B
                            stat = "@" + screenName + " " + stat
                            print(stat)
                            print(type(stat))

                            api.update_status(
                                status=stat, in_reply_to_status_id=tweetID)
                            db.updateUser(uid, 'active', board)
                            print(
                                f'Replied to @{screenName}')
                elif userResponse in keywords:
                    # if it is not an integer, check if one of predefined options:
                    print("here")

                    # "scoreboard"
                    if userResponse == 'scoreboard':
                        loss, wins = db.queryScoreboard(uid)
                        if not loss:
                            my_reply = api.update_status(
                                status=f'@{screenName} Hey! Here is your personal scoreboard: \n{loss} losses || {wins} wins!', in_reply_to_status_id=tweetID)
                        else:
                            my_reply = api.update_status(
                                status=f'@{screenName} Hmmm, I could not find your records... Start a new game!', in_reply_to_status_id=tweetID)

                    # "board"
                    elif userResponse == 'board':
                        board = db.queryBoard(uid)
                        if board:
                            print_B = make_board_string(
                                print_twitter_board(dbBoard.importBoard(board)))
                            my_reply = api.update_status(
                                status=f'@{screenName} Hey! Here is the board: \n{print_B}', in_reply_to_status_id=tweetID)
                        else:
                            my_reply = api.update_status(
                                status=f'@{screenName} Hmmm, no active games... Start a new game!', in_reply_to_status_id=tweetID)

                    # "new game"
                    elif userResponse == 'new game':
                        dbItem = db.queryItem(uid)
                        if dbItem['gameStatus'] == 'new' or dbItem['gameStatus'] == 'inactive':
                            my_reply = api.update_status(
                                status=f'@{screenName} New game started, make your move!', in_reply_to_status_id=tweetID)
                            db.updateUser(
                                uid, 'active', board)
                        else:
                            my_reply = api.update_status(
                                status=f'@{screenName} You have forfeited this game. New game started, make your move!', in_reply_to_status_id=tweetID)
                            db.updateUser(
                                uid, 'active', connect4.makeBoard())
                            db.userLose(uid)

                    # "surrender"
                    elif userResponse == 'surrender':
                        dbItem = db.queryItem(uid)
                        if dbItem['gameStatus'] == 'new' or dbItem['gameStatus'] == 'inactive':
                            my_reply = api.update_status(
                                status=f'@{screenName} No game to forfeit, start playing a game first!', in_reply_to_status_id=tweetID)
                        else:
                            my_reply = api.update_status(
                                status=f'@{screenName} You have forfeited this game. Play again any time!', in_reply_to_status_id=tweetID)
                            db.updateUser(
                                uid, 'inactive', connect4.makeBoard())
                            db.userLose(uid)

                else:
                    # Incorrect input, try again.
                    my_reply = api.update_status(
                        status=f'@{screenName} Hey there, invalid tweet! Remember to check our pinned tweet to see how to play!', in_reply_to_status_id=tweetID)

        else:
            print("No New Tweets...")
        time.sleep(20)


# while True:

#     print("~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~")
# user = api.lookup_users(["1622317940"])
cnnct4()

# status = "@friscokiddo Here is the current board! Remember to check our pinned tweet to see how to play!\n"
# res = api.update_status(
#     status=status, in_reply_to_status_id=1485162198150225920)

# print(res)
# new_tweets = get_new_mentions()
# if new_tweets == None:
#     pass
#     else:
#         # Cycle through each tweet, check user and parse text...
#         #       if new user create user in DB and start game
#         #       else, check text to see if valid syntax used for move.
#         #           if yes, makeb move, update board, send to user / DB.
#         #           else, "please make valid move", resend board from db.
#         #
#         pass
#     print("~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~")

#     time.sleep(20)


# latest = api.mentions_timeline()[0]
# print(latest.user.screen_name)
