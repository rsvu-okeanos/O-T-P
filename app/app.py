from common.transactieApi import transactieApi
from common.streepsysteemApi import streepsysteemApi
from stockExchange.app import stockExchangeApp
from tradingPlatform.app import tradingPlatformApp
from flask import Flask, json, request, make_response
import time as t
import requests as r
import os
import yaml

DIR = os.path.dirname(__file__)
CONFIG_FILE = os.path.join(DIR, 'conf/config.yml')
CONFIG = yaml.load(open(CONFIG_FILE))

CASH_USER = CONFIG['system']['cashUser']
TRADING_PROXY = CONFIG['system']['tradingProxy']
URL = CONFIG['system']['systemUrl']

# Initialize the connections to the system
streepsysteem = streepsysteemApi(URL, CASH_USER, TRADING_PROXY)
transacties = transactieApi(URL, streepsysteem)
print("App is running with a time difference of: "+str(transacties.timeDiff))

# Initialize the flask app
app = Flask(__name__)

# We validate that every post request sends us valid JSON
@app.before_request
def before_request():
    if request.method == 'POST' and not ('application/json' in request.headers['Content-Type']):
        return make_response(json.jsonify({'Error': 'Request should be valid JSON'}), 400)
    return None

@app.after_request
def after_request(response):
    response.headers['Access-Control-Allow-Origin'] = '*'
    response.headers['Access-Control-Allow-Headers'] = 'Content-Type, Authorization'
    return response

# Initialize the stockExchange part of the app
stockExchange = stockExchangeApp(app, None, transacties, streepsysteem, CONFIG)

# Initialize the trading platform routes
tradingPlatform = tradingPlatformApp(app, None, streepsysteem, CONFIG)

# Run the flask app
app.run(host="0.0.0.0", port=80, threaded=True)
