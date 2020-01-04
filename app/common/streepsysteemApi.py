import requests as r
import sys
from lxml import etree
import html
import time as t

class streepsysteemApi(object):
	def __init__(self, url, cashUser, proxyId):
		self.proxyId = proxyId
		self.cashUser = cashUser
		self.s = r.Session()
		self.s.auth = 

		self.baseUrl = url

		req = self.s.get(url)
		self.session = req.cookies['SESSION']

		self.usersLastUpdate = 0
		# self.updateLocalUsers()

	def streep(self, productId, userId):
		# First we set our session state to the user we whish
		# to registter our products on
		url = self.baseUrl + "/index.php/select/user"

		querystring = {"user_id":userId}

		headers = {
			'cache-control': "no-cache"
			}

		req  = self.s.get(url, headers=headers, params=querystring)

		self.initial= req

		# Next we register the product we want to register
		url = self.baseUrl + "/index.php/select/product"

		payload = {
			"xajax": "add_purchase",
			"xajaxargs[]": productId
		}

		headers = {
			#'content-type': "multipart/form-data",
			'cache-control': "no-cache"
			}

		req = self.s.post(url, data=payload, headers=headers)

		url = self.baseUrl + "/index.php/select/product"


		# We finish the transaction by comittin it
		querystring = {"action":"streep"}

		headers = {
			'cache-control': "no-cache"
			}

		response = self.s.get(url, headers=headers, params=querystring)

	def __parseUsersPage(self, raw):
		print(raw)
		tree = etree.fromstring(html.unescape(raw).encode())

		#We parse the data for the users
		usersString = tree.xpath('//cmd[@t="user_content"]/text()')
		usersTree = etree.fromstring("<container>"+usersString[0]+"</container>")

		users = usersTree.xpath('//a/text()')
		ids = self.__prepareUserIds(usersTree.xpath('//a/@href'))

		lastPage = not (tree.xpath('//cmd[@t="page_right"]/text()')[0] == 'page_right_wide')

		return {uid: name for uid,name in zip(ids, users)}, lastPage

	def __prepareProductIds(self, ids):
		return [pid[19:-2] for pid in ids]

	def __parseProductsPage(self,raw):
		tree = etree.fromstring(html.unescape(raw.decode('utf-8')).encode())

		productsString = tree.xpath('//cmd[@t="product_content"]/text()')
		productsTree = etree.fromstring("<container>"+productsString[0]+"</container>")

		nameAndPrices = productsTree.xpath('//a/div[@class="photo_title"]/text()')

		names = nameAndPrices[0::2]
		prices = nameAndPrices[1::2]

		ids = self.__prepareProductIds(productsTree.xpath('//a/@onmouseup'))

		return {pid: [name, price] for pid,name, price in zip(ids, names, prices)}

	def __prepareUserIds(self, ids):
		return [uid[9:] for uid in ids]

	def __initSearch(self, searchQuery=None):
		req = self.s.post(self.baseUrl + "/index.php/select/user", data={"xajax": "reset_search"})
		if not (searchQuery == None):
			req = self.s.post(self.baseUrl + "/index.php/select/user", data={"xajax": "search", "xajaxargs[]": searchQuery})
		return req.text

	def __nextUsersPage(self):
		req = self.s.post(self.baseUrl + "/index.php/select/user", data={"xajax": "next_page"})
		return req.text

	def updateLocalUsers(self):
		if self.usersLastUpdate < t.time() - 3600*24:
			self.usersLastUpdate = t.time()

			lastPage = False
			first = True

			users = {}

			while(not lastPage):
				if(first):
					first = False
					newUsers, lastPage = self.__parseUsersPage(self.__initSearch())
				else:
					newUsers, lastPage = self.__parseUsersPage(self.__nextUsersPage())

				users.update(newUsers)
			self.users  = users


	def getUsers(self, searchQuery=None):
		self.updateLocalUsers()

		if searchQuery == None:
			return self.users

		users = {}

		for uid, name in self.users.items():
			if searchQuery in name:
				users.update({uid: name})
		return users

	def findUserById(self, userId):
		self.updateLocalUsers()
		if str(userId) in self.users.keys():
			return self.users[str(userId)]
		return False

	def __nextProductsPage(self):
		req = self.s.post(self.baseUrl + "/index.php/select/product", data={'xajax': 'next_page'})
		return req.content

	def getProducts(self):
		self.s.get(self.baseUrl + "/index.php/select/user", params={"user_id":self.cashUser})

		products = {}

		while(True):
			newProducts = self.__parseProductsPage(self.__nextProductsPage())

			if list(newProducts.keys())[0] in products.keys():
				break;
			else:
				products.update(newProducts)

		return products

	def resetTradingProxy(self):
		self.setPrice(self.proxyId, 0)

	def setPrice(self, productId, price):
		self.s.post(self.baseUrl + "/media/output/set_product_price.php", data={'product_id': productId, 'price': price})

	def sell(self, seller, buyer, ammount):
		self.setPrice(self.proxyId, ammount)
		self.streep(self.proxyId, buyer)

		self.setPrice(self.proxyId, -1*ammount)
		self.streep(self.proxyId, seller)
