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
from random import choice

cv = None
plant_crops = ['plot_candycanes']
weight = 10

def loadState(cv_in):
	global cv
	cv = cv_in
	cv.log('Loading crops plugin state.')

def saveState():
	cv.log('Saving crops plugin state.')

def setup(data):
	cv.log('Setting crops plugin up.')

def harvest(obj):
	if cv.user['energy'] <= 1:
		return cv.log('Not enough energy to harvest')

	cv.log('Harvesting crop (' + obj['contractName'] + ') x=' + str(obj['position']['x']) + ' y=' + str(obj['position']['y']) + ' id:' + str(obj['id']))

	harvest =	{'sequence': cv.getSequence(),
				 'functionName': 'WorldService.performAction',
				 'params': ['harvest', obj, time(), []]}

	response = cv.send([harvest])

def harvestCrops():
	if cv.user['energy'] <= 1:
		return cv.log('Not enough energy to harvest crops.')

	cv.log('=========================')
	cv.log('Harvesting crops.')

	for k, obj in cv.city['objects'].items():
		if obj['className'] == 'Plot' and obj['state'] != 'withered' and obj['state'] != 'plowed' and obj['state'] == 'grown':
			harvest(obj)

	cv.log('Done harvesting.')
	cv.log('=========================')

def clear(obj):
	cv.log('Clearing withered ' + obj['contractName'] + ' x=' + str(obj['position']['x']) + ' y=' + str(obj['position']['y']) + ' id:' + str(obj['id']))

	clear =	{'sequence': cv.getSequence(),
			 'functionName': 'WorldService.performAction',
			 'params': ['clearWithered', obj, time(), []]}

	response = cv.send([clear])

def clearCrops():
	cv.log('=========================')
	cv.log('Clearing withered crops.')

	for k, obj in cv.city['objects'].items():
		if obj['className'] == 'Plot' and obj['state'] == 'withered':
			clear(obj)

	cv.log('Done clearing.')
	cv.log('=========================')

def plant(obj, crop):
	cv.log('Planting crop (' + crop + ') x=' + str(obj['position']['x']) + ' y=' + str(obj['position']['y']))

	obj['state'] = 'planted'
	obj['contractName'] = crop
	obj['itemName'] = 'plot_crop'
	obj['plantTime'] = time() * 1000

	plant =	{'sequence': cv.getSequence(),
			 'functionName': 'WorldService.performAction',
			 'params': ['startContract', obj, []]}

	response = cv.send([plant])

def plantCrops():
	cv.log('=========================')
	cv.log('Planting crops.')

	for k, obj in cv.city['objects'].items():
		if obj['className'] == 'Plot' and obj['state'] == 'plowed':
			plant(obj, choice(plant_crops))

	cv.log('Done planting.')
	cv.log('=========================')

def run():

	harvestCrops()
	clearCrops()
	plantCrops()
