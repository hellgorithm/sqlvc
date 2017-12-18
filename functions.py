import globalvars
import os
import xml.etree.cElementTree as ET
from PyQt5 import QtWidgets, QtGui, QtCore
import pyodbc
import time
from treeModel import treeModel
import tempfile
import subprocess, threading

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

		#configure DB
		continueExec = configureDB(connectWindow)

		#if no errors exeecuting config...continue
		if continueExec:
			getUserObject()

		connectWindow.btnCancel.click()
	else:
		error_message = "Could not connect to database server!"
		QtWidgets.QMessageBox.about(connectWindow, "Error", error_message)

def configureDB(connectWindow):

	connString = ""
	db = dbConn()

	try:
		if globalvars.engine == "Microsoft SQL Server":
			if globalvars.authType == "Windows Authentication":
				connString = "DRIVER={" + globalvars.SQLSERVER + "};SERVER=" + globalvars.server + ";DATABASE=" + globalvars.DBGIT + ";Trusted_Connection=yes;"
			else:
				connString = "DRIVER={" + globalvars.SQLSERVER + "};SERVER=" + globalvars.server + ";DATABASE=" + globalvars.DBGIT + ";UID=" + globalvars.username + ";PWD=" + globalvars.password

			print("stablishing connection to : " + connString)
			conn = pyodbc.connect(connString)
			conn.close()

			print("Database exists")

			globalvars.connString = connString
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

					eventLogger = open("./scripts/MSSQL/03 getLatestScriptByUser.sql", "r")
					sql03 = eventLogger.read()
					eventLogger.close()

					cursor.execute(sql03)

					eventLogger = open("./scripts/MSSQL/04 getScriptByVersions.sql", "r")
					sql04 = eventLogger.read()
					eventLogger.close()

					cursor.execute(sql04)

					eventLogger = open("./scripts/MSSQL/05 getLatestScriptByRowId.sql", "r")
					sql05 = eventLogger.read()
					eventLogger.close()

					cursor.execute(sql05)
					conn.close()

					globalvars.connString = connString
					return True

				elif globalvars.engine == "MySQL":
					print("Not yet supported")

			except Exception as e:
				saveLog(e)
				print("Error creating repository! Please see log file")
				error_message = "Error creating repository! Please see log file"
				reply = QtWidgets.QMessageBox.question(connectWindow, "Install Scripts", error_message,  QtWidgets.QMessageBox.Ok)


				if globalvars.engine == "Microsoft SQL Server":
					conn = pyodbc.connect(globalvars.connTest, autocommit=True)
					cursor = conn.cursor()
					cursor.execute("DROP DATABASE " + globalvars.DBGIT)

					eventLogger = open("./scripts/MSSQL/rollback.sql", "r")
					rollback = eventLogger.read()
					eventLogger.close()

					cursor.execute(rollback)
					
					conn.close()

				elif globalvars.engine == "MySQL":
					print("Not yet supported")

				return False
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
		print(len(instances))
		for instance in reversed(instances):
			connWin.layout.cmbServers.addItem(instance.attrib["instance"])
			index = connWin.layout.cmbAuthType.findText(instance.attrib["authentication"], QtCore.Qt.MatchFixedString)
			if index >= 0:
				connWin.layout.cmbAuthType.setCurrentIndex(index)
			connWin.layout.txtUserName.setText(instance.attrib["user"])

def getUserObject():

	if globalvars.engine == "Microsoft SQL Server":
		conn = pyodbc.connect(globalvars.connString)
		cursor = conn.cursor()
		cursor.execute("select * from [SQLVC].[dbo].[UserWorkspace] where LoginName='" + globalvars.username + "'")
		#cursor.execute("select * from [SQLVC].[dbo].[UserWorkspace]")
		rows = cursor.fetchall()

	globalvars.databaseEdits = rows

	conn.close()

	generateView()

def generateView():
	trViewObjects = treeModel()
	trViewObjects.generateView(globalvars.objListTab, globalvars.databaseEdits)

def generateObjectScript(user, database, objType, objName, rowId = None):

	viewObj = ""

	if globalvars.engine == "Microsoft SQL Server":
		if rowId == None:
			query = "exec getLatestScriptByUser '" + user + "','" + database + "','" + objType + "','" + objName + "'"
		else:
			query = "exec getLatestScriptByRowId '" + str(rowId) + "'"


		conn = pyodbc.connect(globalvars.connString)
		cursor = conn.cursor()
		cursor.execute(query)
		rows = cursor.fetchall()
		for row in rows:
			#viewText.document().setPlainText(row[0]);
			viewObj = row[0]

	return viewObj

def generateVersionList(database, objType, objName):

	viewObj = []

	if globalvars.engine == "Microsoft SQL Server":
		query = "exec getScriptByVersions '" + database + "','" + objType + "','" + objName + "'"

		conn = pyodbc.connect(globalvars.connString)
		cursor = conn.cursor()
		cursor.execute(query)
		viewObj = cursor.fetchall()

	return viewObj

def downloadToCompare(user, db1, objType1, objName1, db2, objType2, objName2, compareType):
	compare_directory = str(tempfile.gettempdir()) + "/"
	print(compare_directory)
	obj1 = ""
	obj2 = ""
	name1 = ""
	name2 = ""
	targetDB = ""

	if globalvars.engine == "Microsoft SQL Server":
		if compareType == "compareLatest": #compare your edits to currently applied
			name1 = compare_directory + objName1 + "_LATEST.sql"
			name2 = compare_directory + objName2 + "_LATEST_USERVERSION.sql"
			obj1 = generateObjectScript('', db1, objType1, objName1) #latest version of the script
			obj2 = generateObjectScript(user, db2, objType2, objName2) #latest version of the user
			targetDB = db2

	c1 = open(name1, "w")
	c1.write(obj1)
	c1.close()

	c2 = open(name2, "w")
	c2.write(obj2)
	c2.close()

	exePath = globalvars.sett.layout.readExePath()

	if len(exePath) > 0:
		p = subprocess.Popen([exePath, name1, name2], stdin=subprocess.PIPE, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
		output, err = p.communicate(b"input data that is passed to subprocess' stdin")
		rc = p.returncode
		
		if rc == 0:
			apply_message = "Apply merged files? You cannot push your code unless you owned the lates version."
			reply  = QtWidgets.QMessageBox.question(globalvars.MainWindow, "Install Scripts", apply_message,  QtWidgets.QMessageBox.Ok,  QtWidgets.QMessageBox.Cancel)

			if reply == QtWidgets.QMessageBox.Ok:
				merged = open(name2, "r")
				toApply = merged.read()
				checkForApply(toApply,targetDB)
	else:
		apply_message = "No difftool found. Please define one in Edit > Preferences > Difftool"
		reply  = QtWidgets.QMessageBox.question(globalvars.MainWindow, "Install Scripts", apply_message,  QtWidgets.QMessageBox.Ok,  QtWidgets.QMessageBox.Cancel)


def checkForApply(mergedFile, targetDB):
	try:
		if globalvars.engine == "Microsoft SQL Server":
			if globalvars.authType == "Windows Authentication":
				connString = "DRIVER={" + globalvars.SQLSERVER + "};SERVER=" + globalvars.server + ";DATABASE=" + targetDB + ";Trusted_Connection=yes;"
			else:
				connString = "DRIVER={" + globalvars.SQLSERVER + "};SERVER=" + globalvars.server + ";DATABASE=" + targetDB + ";UID=" + globalvars.username + ";PWD=" + globalvars.password

			conn = pyodbc.connect(connString, autocommit=True)
			cursor = conn.cursor()
			cursor.execute(mergedFile)

	except Exception as e:
		saveLog(e)
		error_message = "Error applying merged file. Please see log file"
		reply = QtWidgets.QMessageBox.question(globalvars.MainWindow, "Apply Merged", error_message,  QtWidgets.QMessageBox.Ok)



# class dbConn():
# 	def connect(self, *args):
# 		self.db_args = locals()

# 		if globalvars.engine == "Microsoft SQL Server":
# 			return pyodbc.connect(self.db_args)












	




