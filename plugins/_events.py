########################################################################
# Project: AutoCV
# Author: Nic Dienstbier
# Date: 10/31/12
# Purpose: CityVille Automation Tool
########################################################################

import os, os.path, sys, logging, imp, md5, traceback, requests
from lxml import etree
from pyamf.remoting.client import RemotingService
from PySide.QtGui import *
from PySide.QtCore import *
from time import time

cv = None
events = {}
weight = 0
count = 0

def loadState(cv_in):
	global cv
	cv = cv_in
	cv.log('Loading events plugin state.')

def saveState():
	cv.log('Saving events plugin state.')

def setup(data):
	cv.log('Setting events plugin up.')

def acceptEvent(url, hash, event_id):
	headers = {'User-Agent': cv.user_agent, 'Referer': cv.referer}
	payload = {'zySnid': cv.zy_snid,
			   'zyAuthHash': cv.zy_authhash,
			   'zySig': cv.zy_sig,
			   'eventIds[]': hash,
			   'all': 'all',
			   'acceptOnly': 'false'}

	r = requests.get(url, params = payload, headers = headers, config = {'verbose': sys.stderr})

	return r

def getEvents():
	global events
	headers = {'User-Agent': cv.user_agent, 'Referer': cv.referer}
	payload = {'zySnid': cv.zy_snid, 'zyAuthHash': cv.zy_authhash, 'zySig': cv.zy_sig}

	r = requests.get(cv.getZscUrl('evt_data.php'), headers = headers, params = payload, config = {'verbose': sys.stderr})

	r.json
	if r.json == None:
		cv.log('No pending requests found in your inbox.')
		return;

	cv.events = r.json
	#cv.log(str(cv.events))

	cv.assembleDataTree()

def processGifts():
	for k, v in cv.events.items():
		data = v['data'][0]
		metadata = v['metadata']

		if metadata['type_id'] not in [13002] or metadata['type_text'] != 'Gifts':
			continue

		cv.log('Processing ' + metadata['type_text'] + ' with hash ' + k + ' from ' + str(metadata['sender']))
		r = acceptEvent(data['button_post'], k, metadata['type_id'])
		event = r.json[0]

		if(event.has_key('success') and event['success'] == True):
			if(event.has_key('itemName')):
				del cv.events[k]
				cv.log('Reward: ' + event['itemName'] + ' [' + str(event['loot']) + ' x' + str(event['lootAmount']) + ']')

def processHelpRequests():
	for k, v in cv.events.items():
		data = v['data'][0]
		metadata = v['metadata']

		if metadata['type_id'] not in [13011]:
			continue

		cv.log('Processing ' + metadata['type_text'] + ' with hash ' + k + ' from ' + str(metadata['sender']))
		r = acceptEvent(data['button_post'], k, metadata['type_id'])
		event = r.json[0]

		if(event.has_key('success') and event['success'] == True):
			if(event.has_key('itemName')):
				del cv.events[k]
				cv.log('Reward: ' + event['itemName'] + ' [' + str(event['loot']) + ' x' + str(event['lootAmount']) + ']')

def processNeighborInvites():
	for k, v in cv.events.items():
		data = v['data'][0]
		metadata = v['metadata']

		if metadata['type_id'] not in [13002, 13043] or metadata['type_text'] != 'Help Requests':
			continue

		cv.log('Processing ' + metadata['type_text'] + ' with hash ' + k + ' from ' + str(metadata['sender']))
		r = acceptEvent(data['button_post'], k, metadata['type_id'])
		event = r.json[0]

		if(event.has_key('success') and event['success'] == True):
			if(event.has_key('itemName')):
				del cv.events[k]
				cv.log('Reward: ' + event['itemName'] + ' [' + str(event['loot']) + ' x' + str(event['lootAmount']) + ']')

def processCrewInvites():
	for k, v in cv.events.items():
		data = v['data'][0]
		metadata = v['metadata']

		if metadata['type_id'] not in [13022]:
			continue

		cv.log('Processing ' + metadata['type_text'] + ' with hash ' + k + ' from ' + str(metadata['sender']))
		r = acceptEvent(data['button_post'], k, metadata['type_id'])
		event = r.json[0]

		if(event.has_key('success') and event['success'] == True):
			if(event.has_key('itemName')):
				del cv.events[k]
				cv.log('Reward: ' + event['itemName'] + ' [' + str(event['loot']) + ' x' + str(event['lootAmount']) + ']')

def processFactoryInvites():
	for k, v in cv.events.items():
		data = v['data'][0]
		metadata = v['metadata']

		if metadata['type_id'] not in [13028]:
			continue

		cv.log('Processing ' + metadata['type_text'] + ' with hash ' + k + ' from ' + str(metadata['sender']))
		r = acceptEvent(data['button_post'], k, metadata['type_id'])
		event = r.json[0]

		if(event.has_key('success') and event['success'] == True):
			if(event.has_key('itemName')):
				del cv.events[k]
				cv.log('Reward: ' + event['itemName'] + ' [' + str(event['loot']) + ' x' + str(event['lootAmount']) + ']')

def processVipRequests():
	for k, v in cv.events.items():
		data = v['data'][0]
		metadata = v['metadata']

		if metadata['type_id'] not in [13050]:
			continue

		cv.log('Processing ' + metadata['type_text'] + ' with hash ' + k + ' from ' + str(metadata['sender']))
		r = acceptEvent(data['button_post'], k, metadata['type_id'])
		event = r.json[0]

		if(event.has_key('success') and event['success'] == True):
			if(event.has_key('itemName')):
				del cv.events[k]
				cv.log('Reward: ' + event['itemName'] + ' [' + str(event['loot']) + ' x' + str(event['lootAmount']) + ']')

def processPartnerRequests():
	for k, v in cv.events.items():
		data = v['data'][0]
		metadata = v['metadata']

		if metadata['type_id'] not in [13061] or metadata['type_text'] != 'Partner Requests':
			continue

		cv.log('Processing ' + metadata['type_text'] + ' with hash ' + k + ' from ' + str(metadata['sender']))
		r = acceptEvent(data['button_post'], k, metadata['type_id'])
		event = r.json[0]

		if(event.has_key('success') and event['success'] == True):
			if(event.has_key('itemName')):
				del cv.events[k]
				cv.log('Reward: ' + event['itemName'] + ' [' + str(event['loot']) + ' x' + str(event['lootAmount']) + ']')

def run():
	getEvents()

	if not isinstance(cv.events, dict):
		return

	processGifts()
	processHelpRequests()
	processNeighborInvites()
	processCrewInvites()
	processFactoryInvites()
	processVipRequests()
	processPartnerRequests()

	cv.app.processEvents()
