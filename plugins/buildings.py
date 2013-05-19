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
min_goods_to_supply = 300
weight = 15

def loadState(cv_in):
	global cv
	cv = cv_in
	cv.log('Loading buildings plugin state.')

def saveState():
	cv.log('Saving buildings plugin state.')

def setup(data):
	cv.log('Setting buildings plugin up.')

def supply(obj):
	if cv.user['goods'] <= min_goods_to_supply:
		return cv.log('Not enough goods to supply.')

	cv.log('Supply (' + obj['itemName'] + ') x=' + str(obj['position']['x']) + ' y=' + str(obj['position']['y']))

	supply =	{'sequence': cv.getSequence(),
	 	 		 'functionName': 'WorldService.performAction',
	 	 		 'enqueueTime': time(),
	 	 		 'params': ['openBusiness', obj, 0, ['goods']]}

	response = cv.send([supply])

	return True

def build(obj):
	if cv.user['energy'] <= 1:
		return cv.log('Not enough energy to build.')

	cv.log('Building (' + obj['targetBuildingName'] + ') stage=' + str(obj['stage']) + ' x=' + str(obj['position']['x']) + ' y=' + str(obj['position']['y']))
	cv.log(str(obj))

	build =		{'sequence': cv.getSequence(),
	 	 		 'functionName': 'WorldService.performAction',
	 	 		 'enqueueTime': time(),
	 	 		 'params': ['build',
	 	 		 	{'components': {},
	 	 		 	 'state': 'stage_0',
	 	 		 	 'direction': 0,
	 	 		 	 'className': obj['className'],
	 	 		 	 'itemName': obj['itemName'],
	 	 		 	 'tempId': -1,
	 	 		 	 'deleted': False,
	 	 		 	 'position': obj['position']
	 	 		 	 },
	 	 		 	 time(),
	 	 		 	 {'itemId': '', 'mapOwner': cv.snuid}
	 	 		 ]}

	response = cv.send([build])

	return True

def collectRent(obj):
	if cv.user['energy'] <= 1:
		return cv.log('Not enough energy to collect rent.')

	cv.log('Collecting rent from (' + obj['itemName'] + ') x=' + str(obj['position']['x']) + ' y=' + str(obj['position']['y']))

	collect =	{'sequence': cv.getSequence(),
			 	 'functionName': 'WorldService.performAction',
			 	 'enqueueTime': time(),
			 	 'params': ['harvest', obj, []]}

	response = cv.send([collect])

	return True

def collectResidences():
	if cv.user['energy'] <= 1:
		return cv.log('Not enough energy to collect from residences.')

	cv.log('=========================')
	cv.log('Collecting from residences')

	for k, obj in cv.city['objects'].items():
		if obj['className'] == 'Residence' and obj['state'] == 'grown':
			if collectRent(obj) != True:
				break

	cv.log('Done collecting from residences.')
	cv.log('=========================')

def collectRevenue(obj):
	if cv.user['energy'] <= 1:
		return cv.log('Not enough energy to collect revenue')

	cv.log('Collecting revenue from (' + obj['itemName'] + ') x=' + str(obj['position']['x']) + ' y=' + str(obj['position']['y']))

	collect =	{'sequence': cv.getSequence(),
			 	 'functionName': 'WorldService.performAction',
			 	 'enqueueTime': time(),
			 	 'params': ['harvest', obj, []]}

	response = cv.send([collect])

	return True

def collectBusinesses():
	if cv.user['energy'] <= 1:
		return cv.log('Not enough energy to collect from businesses.')

	cv.log('=========================')
	cv.log('Collecting from businesses')

	for k, obj in cv.city['objects'].items():
		if obj['className'] == 'Business' and obj['state'] == 'closedHarvestable':
			if collectRevenue(obj) != True:
				break

	cv.log('Done collecting from businesses.')
	cv.log('=========================')

def supplyBusinesses():
	if cv.user['goods'] <= min_goods_to_supply:
		return cv.log('Not enough goods to supply businesses.')

	cv.log('=========================')
	cv.log('Supplying businesses')

	for k, obj in cv.city['objects'].items():
		if obj['className'] == 'Business' and obj['state'] == 'closed':
			if supply(obj) != True:
				break

	cv.log('Done supplying.')
	cv.log('=========================')

def completeBuildings():
	if cv.user['energy'] <= 1:
		return cv.log('Not enough energy to build.')

	cv.log('=========================')
	cv.log('Completing construction')

	for k, obj in cv.city['objects'].items():
		if obj['className'] == 'ConstructionSite' and obj['state'] != 'grown':
			if build(obj) != True:
				break

	cv.log('Finished building')
	cv.log('=========================')

def run():
	""""""
	#collectResidences()
	#collectBusinesses()

	#supplyBusinesses()
	#completeBuildings()
