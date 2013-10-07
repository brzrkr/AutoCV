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
weight = 5

def loadState(cv_in):
	global cv
	cv = cv_in
	cv.log('Loading daily bonus plugin state.')

def saveState():
	cv.log('Saving daily bonus plugin state.')

def setup(data):
	cv.log('Setting daily bonus plugin up.')

def collectDailyBonus():
	cv.log('Collecting daily bonus.')

	collect =	{'sequence': cv.getSequence(),
	 	 		 'functionName': 'UserService.collectDailyBonus',
	 	 		 'params': []}

	response = cv.send([collect])

	cv.log(str(response['data'][0]))

def dailyBonus():
	cv.log('=========================')
	collectDailyBonus()
	cv.log('=========================')

def run():
	dailyBonus()
