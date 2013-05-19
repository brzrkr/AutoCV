########################################################################
# Project: AutoCV
# Author: Nic Dienstbier
# Date: 10/31/12
# Purpose: CityVille Automation Tool
########################################################################

import sys, logging, re, urlparse
from PySide.QtGui import *
from PySide.QtCore import *
from time import time

cv = None
weight = 1

def loadState(cv_in):
	global cv
	cv = cv_in
	cv.log('Loading light level up plugin state.')

def saveState():
	cv.log('Saving light level up plugin state.')

def setup(data):
	cv.log('Setting light level up plugin up.')

def lightLevelUp():
	cv.log('Lighting level up.')

	light =	{'sequence': cv.getSequence(),
 	 		 'functionName': 'UserService.lightLevelUp',
 	 		 'enqueueTime': time(),
 	 		 'stamp': time(),
 	 		 'params': []}

	response = cv.send([light])
	cv.log(str(response))

def run():
	cv.log('=========================')
	lightLevelUp()
	cv.log('=========================')
