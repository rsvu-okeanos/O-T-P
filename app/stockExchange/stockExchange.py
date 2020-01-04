import numpy as np
import threading
import time as t

class stockExchange(object):
	def __init__(self, products, updatesCallback,
					fluctuationPerc = 0.02, volatilityPerc = 0.1,
					reversion = 0.3, balancingFactor = None, declineTime = None):
		self.products = products

		# Keep track of the initial price. We will revert to this eventually
		for key, product in self.products.items():
			self.products[key]['base_price'] = product['price']

		self.updatesCallback = updatesCallback
		self.purchaseTimes = []
		self.volatilityPerc = volatilityPerc
		self.fluctuationPerc = fluctuationPerc
		self.reversion = reversion
		self.declineTime = declineTime
		self.n = len(self.products) if balancingFactor == None else balancingFactor

		self.__initializeProducts()

	def setCallback(self, callback):
		self.updatesCallback = callback

	def setFundamental(self, productId, value):
		if productId in self.products.keys() and value > self.products[productId]['min'] and value < self.products[productId]['max']:
			self.products[productId]['fundamental'] = value
		else:
			return False
		return True

	def getPrice(self, productId):
		if productId in self.products.keys():
			return self.products[productId]['price']
		return False


	def __initializeProducts(self):
		for key, product in self.products.items():
			self.products[key]['fundamental'] = product['price']
			self.products[key]['lastTransaction'] = t.time()
			self.products[key]['vol'] = 0
			self.products[key]['delta'] = 0

	def fundamentalUp(self, key):
		percentage = (1+self.fluctuationPerc)
		self.products[key]['fundamental'] = self.products[key]['fundamental']*percentage

	def fundamentalDown(self, key):
		percentage = (1-self.fluctuationPerc)**(self.products[key]['importanceFactor']/self.n)
		print("percentage decrease for product %s: %.3f" % (key, percentage))
		self.products[key]['fundamental'] = self.products[key]['fundamental']*percentage

	def __volumeUp(self, key):
		self.products[key]['vol'] += 1

	def __resetVolumes(self):
		for key, product in self.products.items():
			self.products[key]['vol'] = 0

	def __updateFundamentalsAndVolume(self, transaction):
		for key, product in self.products.items():
			if transaction['product_id'] == key:
				self.__volumeUp(key)
				self.fundamentalUp(key)
			else:
				self.fundamentalDown(key)

	def __updatePrices(self):
		for key, product in self.products.items():
			logPrice = np.log(product['price'])
			logFundamental = np.log(product['fundamental'])
			shock = np.random.randn(1)[0] * logFundamental * self.volatilityPerc

			newLogPrice = logPrice + -1 * self.reversion * (logPrice - logFundamental)
			newPrice = min(max(product['min'], np.exp(newLogPrice)), product['max']) + shock
			self.products[key]['delta'] = newPrice - self.products[key]['price']
			self.products[key]['price'] = newPrice

			# We will revert to the base fundatemental so that product will not remain too
			# cheep or too expensive for a too long time
			self.products[key]['fundamental'] = (
				self.products[key]['fundamental'] 
				+ (1/self.products[key]['reversion_periods']) 
				* (self.products[key]['base_price'] - self.products[key]['fundamental'])
			)

	def __processTransactions(self, transactions):
		self.__resetVolumes()
		for transaction in transactions:
			self.__updateFundamentalsAndVolume(transaction)

		self.__updatePrices()

	def __pushPrices(self):
		# Some processing goes here
		if not (self.updatesCallback == None):
			self.updatesCallback(self.products)

	def market(self, transactions):
		self.__processTransactions(transactions)
		self.__pushPrices()
