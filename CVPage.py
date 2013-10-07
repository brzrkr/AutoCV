########################################################################
# Project: AutoCV
# Author: Nic Dienstbier
# Date: 10/31/12
# Purpose: CityVille Automation Tool
########################################################################

import sys, logging
from PySide.QtWebKit import *
from PySide.QtNetwork import *
from PySide.QtGui import *
from PySide.QtCore import *

class CVPage(QWebPage):
	def __init__(self, parent = None, cv = None):
		super(CVPage, self).__init__(parent)
		self.cv = cv
		self.loaded = False

	def acceptNavigationRequest(self, frame, req, nav_type):
		if self.loaded == True:
			return super(CVPage, self).acceptNavigationRequest(frame, req, nav_type)

		url = req.url()

		if url.hasQueryItem('zySig') and url.hasQueryItem('zyAuthHash') and url.hasQueryItem('zySnid'):
			self.zy_sig = str(url.queryItemValue('zySig'))
			self.zy_authhash = str(url.queryItemValue('zyAuthHash'))
			self.zy_snid = str(url.queryItemValue('zySnid'))
			self.referer = str(url.toString())
			self.user_agent = str(req.rawHeader('User-Agent'))

			self.loaded = self.cv.setHeader(self.zy_sig, self.zy_authhash, self.zy_snid, self.referer, self.user_agent)

		return super(CVPage, self).acceptNavigationRequest(frame, req, nav_type)

