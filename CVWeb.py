########################################################################
# Project: AutoCV
# Author: Nic Dienstbier
# Date: 10/31/12
# Purpose: CityVille Automation Tool
########################################################################

import sys, logging
import re
from urlparse import urlparse
from PySide.QtWebKit import *
from PySide.QtNetwork import *
from PySide.QtGui import *
from PySide.QtCore import *
from CVBot import *
from CVWeb import *
from CVPage import *

class CookieJar(QNetworkCookieJar):
	def __init__(self, parent = None):
		#QNetworkCookieJar.__init__(self, parent)
		super(CookieJar, self).__init__(parent)

	def allCookies(self):
		return QNetworkCookieJar.allCookies(self)

	def setAllCookies(self, cookieList):
		QNetworkCookieJar.setAllCookies(self, cookieList)

class CVWeb(QWebView):
	def __init__(self, parent = None, cv = None):
		super(CVWeb, self).__init__(parent)

		self.loadFinished.connect(self.onFinish)
		self.loadStarted.connect(self.onStart)
		self.page().frameCreated.connect(self.onFrame)
		self.loadProgress.connect(self.onProgress)

		self.cv = cv
		self.cookie_jar = CookieJar()
		self.setPage(CVPage(None, cv))


		settings = self.settings()
		settings.setAttribute(QWebSettings.PluginsEnabled, False)
		settings.setAttribute(QWebSettings.JavaEnabled, False)
		settings.setAttribute(QWebSettings.JavascriptCanOpenWindows, True)
		settings.setAttribute(QWebSettings.JavascriptCanAccessClipboard, True)
		settings.setAttribute(QWebSettings.DeveloperExtrasEnabled, False)
		settings.setAttribute(QWebSettings.ZoomTextOnly, False)
		settings.setIconDatabasePath ('./data')
		settings.setOfflineStoragePath('./data')
		settings.enablePersistentStorage('./data')

		file = QFile('./data/cookies.bin')
		if file.open(QIODevice.ReadOnly):
			ba = file.readAll()
			self.restoreState(ba)
		file.close()

		self.page().networkAccessManager().setCookieJar(self.cookie_jar)

	def onProgress(self, progress):
		if self.cv.hasLoaded() == False:
			self.cv.ui.text_browser.setText("Loading Data: " + str(progress) + "%")

			for child in self.page().mainFrame().childFrames():
				au_matches = re.search("var VERSIONED_ASSET_URL = '(.*?)'", child.toHtml())
				sid_matches = re.search("\"unique_session_key\":\"(.*?)\"", child.toHtml())
				gu_matches = re.search("var APP_URL = \"(.*?)\"", child.toHtml())

				if au_matches != None and sid_matches != None and gu_matches != None:
					self.flash_revision = au_matches.group(1).split("/")[-2]
					#self.cv.setVersionedAssetUrl(au_matches.group(1))
					self.cv.setGateway(gu_matches.group(1))
					self.cv.setFlashRevision(self.flash_revision)
					self.cv.setSessionUid(sid_matches.group(1))

					file = QFile('./data/cookies.bin')
					if file.open(QIODevice.WriteOnly):
						file.write(self.saveState())
					file.close()

					self.cv.start()

	def onFinish(self, ok):

		file = QFile('./data/cookies.bin')
		if file.open(QIODevice.WriteOnly):
			file.write(self.saveState())
		file.close()

	def onStart(self):
		""""""

	def onFrame(self, frame):
		print 'Frame Created: ', frame.frameName()

	def saveState(self):
		cookie_list = self.cookie_jar.allCookies()
		raw = []

		for cookie in cookie_list:
			# We don't want to store session cookies
			if cookie.isSessionCookie():
				continue

			# Store cookies in a list as a dict would occupy
			# more space and we want to minimize network bandwidth
			isHttpOnly = str(cookie.isHttpOnly())

			raw.append([
				str(cookie.name().toBase64()),
				str(cookie.value().toBase64()),
				unicode(cookie.path()).encode('utf-8'),
				unicode(cookie.domain()).encode('utf-8'),
				unicode(cookie.expirationDate().toString()).encode('utf-8'),
				str(isHttpOnly),
				str(cookie.isSecure()),
			])

		return QByteArray(str(raw))

	def restoreState(self, value):
		if not value:
			return

		raw = eval(str(value))
		cookie_list = []

		for cookie in raw:
			name = QByteArray.fromBase64(cookie[0])
			value = QByteArray.fromBase64(cookie[1])
			network_cookie = QNetworkCookie(name, value)
			network_cookie.setPath(unicode(cookie[2], 'utf-8'))
			network_cookie.setDomain(unicode(cookie[3], 'utf-8'))
			network_cookie.setExpirationDate(QDateTime.fromString(unicode(cookie[4], 'utf-8')))

			network_cookie.setHttpOnly(eval(cookie[5]))
			network_cookie.setSecure(eval(cookie[6]))
			cookie_list.append(network_cookie)

		self.cookie_jar.setAllCookies(cookie_list)
		self.page().networkAccessManager().setCookieJar(self.cookie_jar)
