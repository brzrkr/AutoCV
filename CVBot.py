########################################################################
# Project: AutoCV
# Author: Nic Dienstbier
# Date: 10/31/12
# Purpose: CityVille Automation Tool
########################################################################

import os, os.path, sys, logging, imp, md5, traceback, requests, time
from lxml import etree
from pyamf.remoting.client import RemotingService
from PySide.QtUiTools import *
from PySide.QtCore import *
from PySide.QtGui import *
from CVBot import *
from CVWeb import *
from CVPage import *
from mainui import *

class HeartbeatThread(QThread):
	def __init__(self, parent = None, cv = None):
		super(HeartbeatThread, self).__init__(parent)
		self.cv = cv

	def run(self):
		self.cv.started = True
		while self.cv.started:
			self.heartbeat()
			self.msleep(self.cv.interval)

	def stop(self, wait = False):
		self.cv.started = False
		if wait:
			self.wait()

	def heartbeat(self):
		self.cv.refreshZy()
		self.cv.app.processEvents()

		for plugin in self.cv.plugins:
			plugin.run()
			self.cv.app.processEvents()
			self.msleep(1000)

		self.msleep(1000)
		self.cv.app.processEvents()

class CVBot():
	def __init__(self, main_window = None, app = None):
		self.main_window = main_window
		self.app = app

		# connection information
		self.app_url = 'http://apps.facebook.com/cityville/flash.php'
		self.gateway_url = 'http://web-zc1.cityville.zynga.com/'
		self.asset_url = 'http://fb-zc1.cityville.zynga.com/'
		self.thread = HeartbeatThread(None, self)
		self.data_dir = './data/'
		self.plugins_dir = './plugins/'

		# Zynga Header / Authentication Default
		self.zy_authhash = None
		self.zy_snid = None
		self.zy_sig = None
		self.snuid = None
		self.referer = None
		self.user_agent = None
		self.flash_revision = None
		self.sequence = 0

		# Initialize our UI
		self.ui = Ui_mainWindow()
		self.ui.setupUi(main_window, self)
		self.main_window.show()
		self.main_window.raise_()

		# default game data
		self.plugins = []
		self.user = {}
		self.city = {}
		self.events = {}
		self.neighbors = {}
		self.started = False
		self.loaded = False
		self.interval = 1800000/2

		# Start loading facebook and game
		self.log('Loading: ' + self.app_url)
		self.ui.web_view.load(QUrl(self.app_url))

		self.ui.tree_widget.itemExpanded.connect(self.onExpansion)

		# load plugins
		self.loadPlugins(self.plugins_dir)

	def log(self, msg):
		self.ui.text_browser.append(msg)
		print msg
		#self.app.processEvents()

	def hasStarted(self):
		return self.started

	def hasLoaded(self):
		return self.loaded

	def setGateway(self, url):
		self.gateway_url = url + '/flashservices/gateway.php'

	def getGateway(self):
		return self.gateway_url

	def setAssetUrl(self, url):
		self.asset_url = url

	def getAssetUrl(self):
		return self.asset_url

	def getVersionedAssetUrl(self, file):
		return 'http://cityvillefb.static.zgncdn.com/' + self.flash_revision + '/' + file

	def getZscUrl(self, file):
		return self.getAssetUrl() + 'zsc/' + file

	def getSequence(self):
		self.sequence = self.sequence + 1
		return self.sequence

	def setSequence(self, sequence):
		self.sequence = sequence

	def setSessionUid(self, snuid):
		self.snuid = snuid

	def getSessionUid(self, snuid):
		return self.snuid

	def setFlashRevision(self, flash_revision):
		self.flash_revision = flash_revision

	def getFlashRevision(self, flash_revision):
		return self.flash_revision

	def refreshZy(self):
		url = self.getAssetUrl() + 'session.json'
		params = {'zySig': self.zy_sig, 'zySnid': self.zy_snid, 'zyAuthHash': self.zy_authhash, 'action': 'refreshSig'}
		headers = {'User-Agent': self.user_agent, 'Referer': self.referer, 'Content-Type': 'application/xml', 'Accept': 'application/json', 'X-Requested-With': 'XMLHttpRequest'}

		r = requests.post(url, headers = headers, params = params, config = {'verbose': sys.stderr})
		if r.json is not None:
			self.setHeader(r.json['zySig'], r.json['zyAuthHash'], r.json['zySnid'], self.referer, self.user_agent)

	def setHeader(self, zy_sig, zy_authhash, zy_snid, referer, user_agent):
		self.zy_authhash = zy_authhash
		self.zy_snid = zy_snid
		self.zy_sig = zy_sig
		self.referer = referer
		self.user_agent = user_agent

		return True

	def getHeader(self):
		return {'zyAuthHash': self.zy_authhash, 'zySig': self.zy_sig, 'zySnid': self.zy_snid, 'flashRevision': self.flash_revision}

	def assembleChildren(self, parent_item, cur_item):
		output = []

		if isinstance(cur_item, dict):
			for k, v in cur_item.items():
				item = TreeItem(parent_item, True)
				item.setText(0, str(k))

				if not isinstance(v, dict) and not isinstance(v, tuple) and not isinstance(v, list):
					if not isinstance(v, unicode) and (isinstance(v, int) or isinstance(v, float)):
						item.setText(1, str(v))
					else:
						item.setText(1, v)

				output.append(item)
				self.assembleChildren(item, v)

		elif isinstance(cur_item, list) or isinstance(cur_item, tuple):
			count = 0
			for child in cur_item:
				item = TreeItem(parent_item, True)

				if not isinstance(child, dict) and not isinstance(child, tuple) and not isinstance(child, list):
					item.setText(0, str(child))
				else:
					item.setText(0, str(count))
					count = count + 1

				output.append(item)
				self.assembleChildren(item, child)

		return output

	def assembleDataTree(self):
		self.ui.tree_widget.clear()

		items = []
		for name in 'user city neighbors events'.split():
			if eval('self.' + name) == None:
				continue

			item = QTreeWidgetItem(None, False)
			item.setText(0, name)
			item.addChildren(self.assembleChildren(item, eval('self.' + name)))
			items.append(item)

		self.ui.tree_widget.addTopLevelItems(items)
		#self.ui.tree_widget.resizeColumnToContents(0);
		#self.ui.tree_widget.resizeColumnToContents(1);

		#self.log('Data tree assembled.')

	def onExpansion(self, item):
		self.ui.tree_widget.resizeColumnToContents(0);
		self.ui.tree_widget.resizeColumnToContents(1);


	def loadXml(self):
		for file in 'gameSettings effectsConfig'.split():
			filename = self.data_dir + file + '.xml'
			if os.path.exists(filename):
				continue

			headers = {'User-Agent': self.user_agent}
			response = requests.get(self.getVersionedAssetUrl(file) + '.xml', headers = headers, config = {'verbose': sys.stderr})

			with open(filename, 'wb') as fh:
				fh.write(response.content)

			setattr(self, file, etree.parse(filename))

			self.log("Downloaded: " + file)

	def loadModule(self, path):
		try:
			try:
				fin = open(path, 'rb')

				return imp.load_source(md5.new(path).hexdigest(), path, fin)
			finally:
				try:
					fin.close()
				except:
					pass
		except ImportError, x:
			traceback.print_exc(file = sys.stderr)
			raise
		except:
			traceback.print_exc(file = sys.stderr)
			raise

	def loadPlugins(self, path = "./plugins"):
		for root, dirs, files in os.walk(path):
			for f in files:
				fullpath = os.path.join(root, f)

				if f[0] is not '.' and f[0] is not '_' and f[-1] is not 'c':
					self.plugins.append(self.loadModule(fullpath))

		self.plugins = sorted(self.plugins, key = lambda x: x.weight)

		for plugin in self.plugins:
			plugin.loadState(self)


	def savePlugins(self):
		for plugin in self.plugins:
			plugin.saveState()

	def start(self):
		self.error = None

		self.log('=========================')
		self.log('zySig: ' + self.zy_sig)
		self.log('zyAuthHash: ' + self.zy_authhash)
		self.log('zySnid: ' + self.zy_snid)
		self.log('referer: ' + self.referer)
		self.log('user-agent: ' + self.user_agent)
		self.log('=========================')

		self.gw = RemotingService(self.getGateway(), referer = self.referer, user_agent = self.user_agent)
		self.gw.addHTTPHeader('Accept-Language', 'en-us,en')
		self.gw.addHTTPHeader('Accept-Encoding', 'deflate')
		self.gw.addHTTPHeader('Referer', self.referer)
		self.gw.addHTTPHeader('User-Agent', self.user_agent)

		self.base_service = self.gw.getService('BaseService')

		init_user =		{'secureRandSync': 0,
						 'functionName': 'UserService.initUser',
						 'sequence': self.getSequence(),
						 'params': [self.snuid]}

		init_neighbors = {'sequence': self.getSequence(),
						  'functionName': 'UserService.initNeighbors',
						  'params': []}

		response = self.send([init_user, init_neighbors])

		if response['data'] == None or response['data'][0] == None or response['data'][0]['data'] == None:
			return False

		data = response['data'][0]['data']
		data2 = response['data'][1]['data']

		self.zy_uid = data['userInfo']['id']
		self.zy_snuid = self.zy_uid
		self.city['name'] = data['userInfo']['worldName']
		self.user['socialLevel'] = data['userInfo']['player']['socialLevel']
		self.user['level'] = data['userInfo']['player']['level']
		self.user['gold'] = data['userInfo']['player']['gold']
		self.user['cash'] = data['userInfo']['player']['cash']
		self.user['xp'] = data['userInfo']['player']['xp']
		self.user['energy'] = data['userInfo']['player']['energy']
		self.user['energyMax'] = data['userInfo']['player']['energyMax']
		#self.neighbors = data['userInfo']['player']['neighbors']
		self.neighbors = data2['neighbors']
		self.city['franchises'] = data['franchises']
		self.user['inventory'] = data['userInfo']['player']['inventory']
		self.user['collections'] = data['userInfo']['player']['collections']
		self.user['wishlist'] = data['userInfo']['player']['wishlist']
		self.user['goods'] = data['userInfo']['player']['commodities']['storage']['goods']
		self.city['trains'] = data['featureData']['trains']['workers']

		self.city['objects'] = data['userInfo']['world']['objects']
		self.user['visitor_help'] = data['userInfo']['player']['Orders']['order_visitor_help']['received']['pending']

		self.loadXml()

		for plugin in self.plugins:
			plugin.setup(response['data'])

		self.assembleDataTree()
		self.printWelcome()

		self.ui.start_button.setEnabled(True)

		self.loaded = True

		return True

	def send(self, messages):
		response = self.base_service.dispatchBatch(self.getHeader(), messages, 0)
		self.checkResponse(response)
		self.updateFromResponse(response)

		return response

	def updateFromResponse(self, data):
		if data['data'] == None or data['data'][0] == None:
			return

		changed = False
		metadata = data['data'][0]['metadata']
		initial_state = final_state = None

		if 'finalState' in data['data'][0] and 'initialState' in data['data'][0] and data['data'][0]['finalState'] != None and data['data'][0]['initialState'] != None:
			initial_state = data['data'][0]['initialState']
			final_state = data['data'][0]['finalState']

		# we received a world update, merge the updates with the old objects
		if 'worldUpdate' in metadata and 'objects' in metadata['worldUpdate'] and metadata['worldUpdate']['objects'] != None:
			for id, obj in metadata['worldUpdate']['objects'].items():
				self.city['objects']['w' + id] = obj

			changed = True

		#we received a final state, update user info
		if initial_state != None and final_state != None and initial_state['energy'] != None and final_state['energy'] != None:
			self.user['energy'] = final_state['energy']
			self.user['xp'] = final_state['xp']
			self.user['gold'] = final_state['gold']
			self.user['cash'] = final_state['cash']

			changed = True

		if changed:
			self.assembleDataTree()

	def checkResponse(self, data):
		self.error = ''

		if data['data'] != None:
			if 'errorData' in data['data'][0] and data['data'][0]['errorData'] != None and data['data'][0]['errorData'] != '':
				self.error = data['data'][0]['errorData']
				self.sequence = self.sequence - 1

			if data['data'][0]['data'] != None:
				if 'result' in data['data'][0]['data']:
					if data['data'][0]['data']['result'] is 'failure':
						self.error = 'Unknown error'
						self.sequence = self.sequence - 1
					if data['data'][0]['data']['result'] is 'batchFailure':
						self.error = 'Unknown batchFailure error'
						self.sequence = self.sequence - 1
					if data['data'][0]['data']['result'] is 'success':
						self.log('SUCCESS')


		if 'faultCode' in data and data['faultCode'] != None:
			self.error = data['faultCode']
			self.sequence = self.sequence - 1
		if 'errorData' in data and data['errorData'] != None:
			self.error = data['errorData']
			self.sequence = self.sequence - 1

		if self.error == 'The user does not have enough energy':
			self.user['energy'] = 0
		if self.error == 'Unable to add supply':
			self.user['goods'] = 0
		if self.error == 'Bonus already collected':
			""""""

		if self.error != None and self.error != '':
			self.log(self.error)

	def printWelcome(self):
		self.log('=========================')
		self.log('City Name: ' + self.city['name'])
		self.log('Social Level: ' + str(self.user['socialLevel']))
		self.log('Level: ' + str(self.user['level']))
		self.log('Gold: ' + str(self.user['gold']))
		self.log('Goods: ' + str(self.user['goods']))
		self.log('Cash: '+ str(self.user['cash']))
		self.log('XP: ' + str(self.user['xp']))
		self.log('Energy: ' + str(self.user['energy']) + ' / ' + str(self.user['energyMax']))
		self.log('End User Information')
		self.log('=========================')

		self.log('\n\nWaiting to be started.')

	def run(self):
		if self.started == False:
			self.log('Bot started!')
			self.ui.start_button.setEnabled(False)
			self.ui.stop_button.setEnabled(True)
			self.thread.run()

	def stop(self):
		if self.started == True:
			self.log('Bot stopped!')
			self.ui.start_button.setEnabled(True)
			self.ui.stop_button.setEnabled(False)
			self.thread.stop()

class TreeItem(QTreeWidgetItem):
    def __init__(self, parent, sortable = False):
        QTreeWidgetItem.__init__(self, parent)
        self.sortable = sortable

    def __lt__(self, other):
        #if self.sortable:
            #return QTreeWidgetItem.__lt__(self, other)
        return False
