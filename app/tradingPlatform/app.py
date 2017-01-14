from flask import request, make_response, abort, session, json
from hashlib import md5
import jwt
import time as t
from uuid import uuid1
from common.httpExceptions import *

class tradingPlatformApp(object):
    def __init__(self, flask, socketIO, systemApi, config):
        self.config = config
        self.flask = flask
        self.socketIO = socketIO
        self.systemApi = systemApi

        self.clients = {}

        self.__initRoutes()

        self.transactions = {}

    def __authorizeUser(self, userId):
        userName = self.systemApi.findUserById(userId)
        token = jwt.encode({'id': userId}, self.config['security']['appSecret'], algorithm='HS256').decode('utf-8')
        self.clients[userId] = {
            'userName': userName,
            'token': token
        }

        return token

    def __checkAuthenticationKey(self, authenticationKey):
        givenChecksum = authenticationKey[0:2]
        uId = authenticationKey[2:]

        checksum = md5((uId + self.config['security']['appSecret']).encode()).hexdigest()

        if checksum[0:2] == givenChecksum and self.systemApi.findUserById(uId):
            return int(uId)

        # Better go brew coffee if you are not able to pass a valid authenticationKey :)
        raise ImATeapot('No valid AuthenticationKey was passed.')

    def __checkAuthenticated(self, requestMade):
        if 'Authorization' in requestMade.headers.keys():
            try:
                payload = jwt.decode(
                    requestMade.headers['Authorization'],
                    self.config['security']['appSecret'],
                    algorithm='HS256'
                )
            except :
                raise Unauthorized("Token could not be validated.")

            if 'id' in payload.keys() and int(payload['id']) in self.clients.keys():
                return int(payload['id'])
        raise Unauthorized("Valid Token but users seems not signed in.")

    def __getActiveUsers(self, queryString):
        users = {}
        for key, user in self.clients.items():
            if queryString in user['userName']:
                users.update({key: user['userName']})
        return users

    def __getPendingTransactions(self, uid):
        transactions = {}

        for tid, transaction in self.transactions.items():
            if transaction['buyerId'] == uid:
                transactions[tid] = transaction

        return transactions

    def __initRoutes(self):
        # Users endpoints
        @self.flask.route('/users/search/<string:username>')
        def search(username):
            uid = self.__checkAuthenticated(request)
            return make_response(json.jsonify(self.__getActiveUsers(username)), 200)

        @self.flask.route('/users/list')
        def list():
            uid = self.__checkAuthenticated(request)

            users = [{'id': uKey, 'name': user['userName']} for uKey, user in self.clients.items() if not uKey == uid]
            return make_response(json.jsonify(users), 200)

        @self.flask.route('/users/authenticate', methods=['POST'])
        def authenticate():
            reqJson = request.get_json()
            if not ('authenticationKey' in reqJson.keys()) or len(reqJson['authenticationKey']) < 3:
                raise BadRequest('No AuthenticationKey was passed.')

            uId = self.__checkAuthenticationKey(reqJson['authenticationKey'])
            token = self.__authorizeUser(uId)
            return make_response(json.jsonify({"Token": token}))

        @self.flask.route('/users/authenticationKeys/<string:username>')
        def authenticationKeys(username):
            users = self.systemApi.getUsers(username)

            for key, user in users.items():
                checksum = md5((str(key) + self.config['security']['appSecret']).encode()).hexdigest()
                users[key] = {
                    'userName': user,
                    'authorizationKey': checksum[0:2] + str(key)
                }
            return json.jsonify(users)

        #Transactions endpoints
        @self.flask.route('/transactions/new/<int:buyerId>', methods=['POST'])
        def newTransaction(buyerId):
            uid = self.__checkAuthenticated(request)
            reqJson = request.get_json()

            if not (reqJson.keys() & {'transactionName', 'amount'} and type(reqJson['amount']) == int and reqJson['amount'] >= 0):
                raise BadRequest()
            elif not buyerId in self.clients.keys():
                raise BadRequest('Intended buyer does not exist.')
            else:
                transactionId = str(uuid1())
                reqJson.update({
                    'buyerId': buyerId,
                    'sellerId': uid
                })
                self.transactions[transactionId] = reqJson

                return make_response(json.jsonify({"Response": "Transaction submitted"}), 200)

        @self.flask.route('/transactions/pending')
        def pendingTransactions():
            uid = self.__checkAuthenticated(request)

            return make_response(json.jsonify(self.__getPendingTransactions(uid)), 200)

        @self.flask.route('/transactions/approve/<string:transactionId>')
        def approveTransaction(transactionId):
            uid = self.__checkAuthenticated(request)

            if not transactionId in self.transactions.keys():
                raise BadRequest('Transaction does not exist')

            transaction = self.transactions[transactionId]

            if not uid == transaction['buyerId']:
                raise Unauthorized('Cannot approve transaction in which client is not the buyer.')

            self.systemApi.sell(transaction['sellerId'], transaction['buyerId'], transaction['amount'])
            self.transactions.pop(transactionId)

            return make_response(json.jsonify({"Response": "Transaction processed."}), 200)
