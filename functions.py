import globalvars
import os
import xml.etree.cElementTree as ET
from PyQt5 import QtWidgets, QtGui, QtCore
import pyodbc
import time

def EventEmmitter(index):
	# item = trViewObjects.model().index(0,0)
	# strData = item.data(0).toPyObject()
	# print('' + str(strData))

    item = index.selectedIndexes()[0]

def OpenConnection(connectWindow):
	#save connection for later use
	serverType = connectWindow.cmbDbase.currentText()
	server = connectWindow.cmbServers.currentText()
	username = connectWindow.txtUserName.text()
	password = connectWindow.txtPassword.text()
	authType = connectWindow.cmbAuthType.currentText()

	stat = testConn(serverType, server, authType, username, password)
	if stat:

		globalvars.engine = serverType
		globalvars.server = server
		globalvars.username = username
		globalvars.password = password
		globalvars.authType = authType

		configPath = os.path.expanduser("~") + "/sqlvc/sqlvc-config.xml"
		saveConfigurations(configPath, connectWindow)
		configureDB(connectWindow)

		connectWindow.btnCancel.click()
	else:
		error_message = "Could not connect to database server!"
		QtWidgets.QMessageBox.about(connectWindow, "Error", error_message)

def configureDB(connectWindow):
	try:
		if globalvars.engine == "Microsoft SQL Server":
			if globalvars.authType == "Windows Authentication":
				connString = "DRIVER={" + globalvars.SQLSERVER + "};SERVER=" + globalvars.server + ";DATABASE=" + globalvars.DBGIT + ";Trusted_Connection=yes;"
			else:
				connString = "DRIVER={" + globalvars.SQLSERVER + "};SERVER=" + globalvars.server + ";DATABASE=" + globalvars.DBGIT + ";UID=" + globalvars.username + ";PWD=" + globalvars.password

			print("stablishing connection to : " + connString)
			conn = pyodbc.connect(connString)
			conn.close()

			print("Database exists success")

			return True
	except Exception as e:
		saveLog(e)
		print("Database does not exists, create one...")
		error_message = "SQLVC scripts not found. Click OK to install."
		reply = QtWidgets.QMessageBox.question(connectWindow, "Install Scripts", error_message,  QtWidgets.QMessageBox.Ok)
		
		if reply == QtWidgets.QMessageBox.Ok:
			#series of steps
			try:
				if globalvars.engine == "Microsoft SQL Server":
					#create db
					conn = pyodbc.connect(globalvars.connTest, autocommit=True)
					cursor = conn.cursor()
					cursor.execute("CREATE DATABASE " + globalvars.DBGIT)

					eventLogger = open("./scripts/MSSQL/01 DDLEvents.sql", "r")
					sql01 = eventLogger.read()
					eventLogger.close()

					cursor.execute(sql01)

					eventLogger = open("./scripts/MSSQL/02 SQLVCEventLogger.sql", "r")
					sql02 = eventLogger.read()
					eventLogger.close()

					cursor.execute(sql02)
					conn.close()
			except Exception as e:
				saveLog(e)
				print("Error creating repository! Please see log file")
				error_message = "Error creating repository! Please see log file"
				reply = QtWidgets.QMessageBox.question(connectWindow, "Install Scripts", error_message,  QtWidgets.QMessageBox.Ok)


				conn = pyodbc.connect(globalvars.connTest, autocommit=True)
				cursor = conn.cursor()
				cursor.execute("DROP DATABASE " + globalvars.DBGIT)

				eventLogger = open("./scripts/MSSQL/rollback.sql", "r")
				rollback = eventLogger.read()
				eventLogger.close()

				cursor.execute(rollback)
				
				conn.close()
		else:
			return False




def testConn(serverType, server, authType, username = None, password = None):
	if serverType == "Microsoft SQL Server":
		try:
			if authType == "Windows Authentication":
				connString = "DRIVER={" + globalvars.SQLSERVER + "};SERVER=" + server + ";DATABASE=" + globalvars.DBTEST + ";Trusted_Connection=yes;"
			else:
				connString = "DRIVER={" + globalvars.SQLSERVER + "};SERVER=" + server + ";DATABASE=" + globalvars.DBTEST + ";UID=" + username + ";PWD=" + password

			print("stablishing connection to : " + connString)
			conn = pyodbc.connect(connString)
			cursor = conn.cursor()
			cursor.execute("SELECT 1")
			row = cursor.fetchall()
			print(len(row))
			conn.close()

			print("Connection success")

			#set engine as SQL Server
			globalvars.engine = globalvars.SQLSERVER
			globalvars.connTest = connString
			return True
		except Exception as e:
			saveLog(e)
			print("Connection error!")
			return False

def saveLog(message):
	log_dir = os.path.expanduser("~") + "/sqlvc/logs/"
	pTime = time.strftime("%m-%d-%Y_%H%M%p")

	if not os.path.isdir(log_dir):
		os.makedirs(log_dir)

	log_obj  = open(log_dir + pTime + ".txt", "w")
	log_obj.write(str(message))
	log_obj.close()


def saveConfigurations(path, connWin = None):

	if os.path.exists(path):
		root = ET.parse(path).getroot()
	else:
		directory = os.path.expanduser("~") + "/sqlvc/"
		
		if not os.path.isdir(directory):
			os.makedirs(directory)

		root = ET.Element("config")

	doc = root.find('instances')
	
	if doc == None:
		doc = ET.SubElement(root, "instances")

	if connWin is not None:
		if str(connWin.cmbServers.currentText()) not in [elem.attrib["instance"] for elem in root.findall('instances/instance')]:
			ET.SubElement(doc, "instance", 
				instance=str(connWin.cmbServers.currentText()),
				authentication = str(connWin.cmbAuthType.currentText()),
				user = str(connWin.txtUserName.text()),
				password='').text = str(connWin.cmbServers.currentText())

	tree = ET.ElementTree(root)
	tree.write(path)

def readConnConfiguration(path, connWin = None):
	if os.path.exists(path):
		root = ET.parse(path).getroot()
		instances = root.findall('instances/instance')

		for instance in instances:
			connWin.layout.cmbServers.addItem(instance.attrib["instance"])
			index = connWin.layout.cmbAuthType.findText(instance.attrib["authentication"], QtCore.Qt.MatchFixedString)
			if index >= 0:
				connWin.layout.cmbAuthType.setCurrentIndex(index)
			connWin.layout.txtUserName.setText(instance.attrib["user"])


