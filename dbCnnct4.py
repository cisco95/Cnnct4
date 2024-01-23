import boto3
from boto3.dynamodb.conditions import Key, Attr
import dbBoard
import connect4
from auth import (
    ACCESS_KEY,
    SECRET_KEY
)

dynamodb = boto3.resource(
    'dynamodb',
    aws_access_key_id=ACCESS_KEY,
    aws_secret_access_key=SECRET_KEY,
    region_name='us-west-1')

users = dynamodb.Table('cnnct4_users')

# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~ CREATE A USER FROM HANDLE: ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~


def createUser(handle):
    board = connect4.makeBoard()
    dbGameBoard = dbBoard.exportBoard(board)

    users.put_item(
        Item={
            'username': handle,
            'gameStatus': 'new',
            'gameBoard': dbGameBoard,
            'winCount': 0,
            'lossCount': 0
        }
    )

    response = users.query(
        KeyConditionExpression=Key('username').eq(handle)
    )
    returnValue = response['Items'][0]

    return returnValue


# createUser("@testUser")
# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~


# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~ UPDATE USER FROM HANDLE: ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
def updateUserStatus(handle, status):
    response = users.update_item(
        Key={
            'username': handle
        },
        UpdateExpression="set gameStatus=:statusUpdated",
        ExpressionAttributeValues={
            ':statusUpdated': status
        },
        ReturnValues="UPDATED_NEW"
    )
    return response


def updateUserBoard(handle, board):
    convertedBoard = dbBoard.exportBoard(board)
    response = users.update_item(
        Key={
            'username': handle
        },
        UpdateExpression="set gameBoard=:newGameBoard",
        ExpressionAttributeValues={
            ':newGameBoard': convertedBoard
        },
        ReturnValues="UPDATED_NEW"
    )
    return response


def userWin(handle):
    winCount = queryItem(handle)['winCount']
    winCount += 1
    response = users.update_item(
        Key={
            'username': handle
        },
        UpdateExpression="set winCount=:newWinCount",
        ExpressionAttributeValues={
            ':newWinCount': winCount
        },
        ReturnValues="UPDATED_NEW"
    )
    return response


def userLose(handle):
    lossCount = queryItem(handle)['lossCount']
    lossCount += 1
    response = users.update_item(
        Key={
            'username': handle
        },
        UpdateExpression="set lossCount=:newLossCount",
        ExpressionAttributeValues={
            ':newLossCount': lossCount
        },
        ReturnValues="UPDATED_NEW"
    )
    return response


def updateUser(handle, status=None, board=None):
    if status is not None:
        updateUserStatus(handle, status)
    if board is not None:
        updateUserBoard(handle, board)


# updateUser('@testUser', 'active', connect4.makeBoard(7))

# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~ QUERY AN ITEM FROM HANDLE: ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
def queryItem(handle):
    response = users.query(
        KeyConditionExpression=Key('username').eq(handle)
    )
    if response['Items']:
        return response['Items'][0]
    else:
        return createUser(handle)


# {"scoreboard", "new game", "board", "surrender"}
# user tweet keywords

def queryScoreboard(handle):
    response = users.query(
        KeyConditionExpression=Key('username').eq(handle)
    )
    if response['Items']:

        returnValue = [response['Items'][0]['lossCount'],
                       response['Items'][0]['winCount']]
    else:
        returnValue = None, None
    return returnValue


def queryBoard(handle):
    response = users.query(
        KeyConditionExpression=Key('username').eq(handle)
    )
    if response['Items'] and response['Items'][0]['gameStatus'] == 'active':
        return response['Items'][0]['gameBoard']
    else:
        return None

# print(queryItem('@testUser')['gameStatus'])
# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
