#!/usr/bin/env python
########################################################################
# Project: AutoCV
# Author: Nic Dienstbier
# Date: 10/31/12
# Purpose: CityVille Automation Tool
########################################################################

cv = None

import sys, logging
from PySide.QtCore import *
from PySide.QtGui import *
from CVBot import *
from CVWeb import *
from CVPage import *

def main(argv = None):
	app = QApplication(sys.argv)
	QObject.connect(app, SIGNAL('lastWindowClosed()'), app, SLOT('quit()'))

	mainWindow = QtGui.QMainWindow()

	cv = CVBot(mainWindow, app)

	sys.exit(app.exec_())

if __name__ == '__main__':
	main()
