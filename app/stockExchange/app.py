from .stockExchange import stockExchange
import requests as r
from flask import request, make_response, abort, session, json
from common.httpExceptions import *
import math

class stockExchangeApp(object):
    def __init__(self, flask, socketIO, transactieApi, systemApi, config):
        self.config = config
        self.flask = flask
        self.socketIO = socketIO
        self.transactieApi = transactieApi
        self.systemApi = systemApi

        self.movies = config['movies']

        self.stockExchange = stockExchange(
            self.config['products'],
            None,
            fluctuationPerc = self.config['market']['fluctuationPerc'],
            volatilityPerc = self.config['market']['volatilityPerc'],
            reversion = self.config['market']['reversion'],
            balancingFactor = self.config['market']['balancingFactor']
        )

        self.__initRoutes()
        self.__initPriceStream()

    def __dictToList(self, toConvert, desiredKey = 'id'):
        return [dict(p, **{desiredKey: key}) for key, p in toConvert.items()]

    def __initRoutes(self):
        @self.flask.route('/setFundamental', methods=['POST'])
        def setFundamental():
            reqJson = request.get_json()

            #Validate the passed parameters
            if not ('id' in reqJson.keys() and 'value' in reqJson.keys()):
                return make_response(json.jsonify({'Error': 'Parameters ID and Value need to be passed.'}), 400)

            if self.stockExchange.setFundamental(reqJson['id'], reqJson['value']):
                return json.jsonify(self.stockExchange.getPrice(reqJson['id']))

            return make_response(json.jsonify({'Error': 'No valid ID was passed.'}), 400)

        @self.flask.route('/getProducts', methods=['GET'])
        def products():
            return make_response(json.jsonify(self.__dictToList(self.stockExchange.products)))

        @self.flask.route('/news')
        def news():
            return make_response(json.jsonify(self.movies), 200)

        @self.flask.route('/news/send/<string:key>')
        def sendNews(key):
            if not key in self.movies.keys():
                raise BadRequest('Movie does not exist')

            self.stockExchange.setFundamental(self.movies[key]['productId'], self.movies[key]['price'])

            r.post("http://localhost:3000/video", json={'id': key})
            return make_response(json.jsonify({'Response': 'Movie was fired.'}), 200)


    def __initPriceStream(self):
        def callback(products):
            frontEndData = [{
                                'id': key,
                                'price': prod['price'],
                                'name': prod['name'],
                                'vol': prod['vol'],
                                'delta': prod['delta']
                            } for key, prod in products.items()]
            # Send off all the data to the node process for pushing it over
            # the socket. Bye Bye
            r.post("http://localhost:3000/newPrices", json=frontEndData)

            for key, prod in products.items():
                self.systemApi.setPrice(key, math.floor(prod['price']*100))

        # Set the callback for price updates
        self.stockExchange.setCallback(callback)

        self.transactieApi.streamData(
            self.config['market']['interval'],
            self.config['market']['safetyMargin'],
            self.stockExchange.market
        )
