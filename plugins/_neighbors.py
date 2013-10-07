########################################################################
# Project: AutoCV
# Author: Nic Dienstbier
# Date: 10/31/12
# Purpose: CityVille Automation Tool
########################################################################

import sys, logging, re, urlparse
from PySide.QtGui import *
from PySide.QtCore import *
from time import *

cv = None
weight = 1

def loadState(cv_in):
	global cv
	cv = cv_in
	cv.log('Loading neighbors plugin state.')

def saveState():
	cv.log('Saving neighbors plugin state.')

def setup(data):
	cv.log('Setting neighbors plugin up.')

def loadNeighbor(nuid, name):
	cv.app.processEvents()

	if nuid == cv.zy_uid or nuid == -1:
		cv.log('Continue')
		return

	cv.log('Loading world id: ' + str(nuid) + ', name: ' + name)

	load_world = {'sequence': cv.getSequence(),
				  'functionName': 'WorldService.loadWorld',
				  'params': [nuid]}

	initial_visit = {'sequence': cv.getSequence(),
		 	 		 'functionName': 'VisitorService.initialVisit',
		 	 		 'params': ['neighborVisit', {'recipientId': nuid, 'senderId': cv.zy_uid}]}

	random_mission = {'sequence': cv.getSequence(),
					  'functionName': "MissionService.getRandomMission",
					  'params': [nuid]}

	response = cv.send([load_world, initial_visit, random_mission])
	cv.log('Received: ' + response['data'][1]['data']['reward']['msg'] + ' (' + str(response['data'][1]['data']['energyLeft']) + ' energy left)')

	#time.sleep(1)
	cv.app.processEvents()
	#time.sleep(1)

	return response

def redeemVisitorHelp(nuid, objects):
	cv.log('Redeeming visitor help from ' + str(nuid))

	funcs = []
	for obj in objects:
		cv.log('Accepting help on (' + str(obj) + ')');

		funcs.append({'sequence': cv.getSequence(),
		 	 		 'functionName': 'VisitorService.redeemVisitorHelpAction',
		 	 		 'params': [nuid, obj]})

	response = cv.send(funcs)

	return response

def acceptHelp():
	for nuid, order in cv.user['visitor_help'].items():
		#cv.log('NUID: ' + nuid + '\nORDER: ' + str(order) + '\n')

		if nuid == None or order.has_key('senderID'):
			nuid = order['senderID']

		if nuid == 'sam' or not order.has_key('status') or not order.has_key('helpTargets'):
			continue

		if order['status'] == "unclaimed" and len(order['helpTargets']) > 0:
			redeemVisitorHelp(nuid, order['helpTargets'])

def loadNeighbors():
	for neighbor in cv.neighbors:
		r = loadNeighbor(neighbor['uid'], neighbor['cityname'])
		#cv.log(str(r))

def run():
	cv.log('=========================')
	loadNeighbors()
	acceptHelp()
	cv.log('=========================')
