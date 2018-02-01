import globalvars
import os, platform
import xml.etree.cElementTree as ET
from PyQt5 import QtWidgets, QtGui, QtCore
import pyodbc
import time
from treeModel import treeModel
import tempfile
import subprocess, threading
import hashlib
import decimal
# from Crypto.Cipher import AES
# from Crypto.Hash import SHA256
import base64
import uuid
import traceback
import keyring


from queries import *


def refreshConn():
	print("refreshing data")
	if globalvars.server != None:
		getUserObject()
		getChangesets()
		getShelve()


def EventEmmitter(index):
	# item = trViewObjects.model().index(0,0)
	# strData = item.data(0).toPyObject()
	# print('' + str(strData))

    item = index.selectedIndexes()[0]

# def OpenConnectionMerge(connectWindow):
# 	try:
# 		serverType = connectWindow.cmbDbase.currentText()
# 		server = connectWindow.cmbServers.currentText()
# 		username = connectWindow.txtUserName.text()
# 		password = connectWindow.txtPassword.text()
# 		authType = connectWindow.cmbAuthType.currentText()

# 		stat = testConn(serverType, server, authType, username, password)
# 		if stat:
# 			configPath = os.path.expanduser("~") + "/sqlvc/sqlvc-config.xml"
# 			saveConfigurations(configPath, connectWindow)

# 			#configure DB
# 			continueExec = configureDB(connectWindow)

# 			#if no errors exeecuting config...continue
# 			if continueExec:
# 				print("Successfully configured database")
# 				globalvars.serverTypeMerge = connectWindow.cmbDbase.currentText()
# 				globalvars.serverMerge = connectWindow.cmbServers.currentText()
# 				globalvars.usernameMerge = connectWindow.txtUserName.text()
# 				globalvars.passwordMerge = connectWindow.txtPassword.text()
# 				globalvars.authTypeMerge = connectWindow.cmbAuthType.currentText()


# 			connectWindow.btnCancel.click()

# 		else:
# 			error_message = "Could not connect to database server!"
# 			QtWidgets.QMessageBox.about(connectWindow, "Error", error_message)

# 	except Exception as e:
# 		saveLog(traceback.format_exc())
# 		print("Connection error occured for merge")

def OpenConnection(connectWindow):
	#save connection for later use
	try:
		serverType = connectWindow.cmbDbase.currentText()
		server = connectWindow.cmbServers.currentText()
		username = connectWindow.txtUserName.text()
		password = connectWindow.txtPassword.text()
		authType = connectWindow.cmbAuthType.currentText()

		stat = testConn(serverType, server, authType, username, password)
		
		if stat == True:

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
				globalvars.MainWindow.parent().setSQLWindowTitle()
				getUserObject()
				getChangesets()
				getShelve()


			connectWindow.btnCancel.click()
		else:
			if stat == "lib":
				error_message = "The driver " + globalvars.SQLSERVER + " is not properly configured."
				QtWidgets.QMessageBox.about(connectWindow, "Error", error_message)
			else:
				error_message = "Could not connect to database server!"
				QtWidgets.QMessageBox.about(connectWindow, "Error", error_message)

	except Exception as e:
		saveLog(traceback.format_exc())
		print("Connection error occured")
		error_message = "Connection error occured. Please see log file for details"
		reply = QtWidgets.QMessageBox.question(connectWindow, "Connection Error", error_message,  QtWidgets.QMessageBox.Ok)

def configureDB(connectWindow):

	connString = ""

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
		saveLog(traceback.format_exc())
		print("Database does not exists, create one...")
		error_message = "SQLVC installation not found. Click OK to install. \n\nYou must be a member of database administrator in order to install SQLVC."
		reply = QtWidgets.QMessageBox.question(connectWindow, "Install Scripts", error_message,  QtWidgets.QMessageBox.Ok)
		
		if reply == QtWidgets.QMessageBox.Ok:
			#series of steps
			try:
				if globalvars.engine == "Microsoft SQL Server":
					#create db
					print("Connectiong to "+ globalvars.connTest)
					query = "CREATE DATABASE " + globalvars.DBGIT
					
					conn = pyodbc.connect(globalvars.connTest, autocommit=True)
					cursor = conn.cursor()
					cursor.execute(query)

					eventLogger = open("./scripts/MSSQL/01 DDLEvents.sql", "r")
					sql01 = eventLogger.read()
					eventLogger.close()

					cursor.execute(sql01)

					eventLogger = open("./scripts/MSSQL/02 SQLVCEventLogger.sql", "r")
					sql02 = eventLogger.read()
					eventLogger.close()

					cursor.execute(sql02)
					conn.close()

					globalvars.connString = connString
					return True

				elif globalvars.engine == "MySQL":
					print("Not yet supported")

			except Exception as e:
				saveLog(traceback.format_exc())
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
			saveLog(traceback.format_exc())
			print("Connection error!")

			if "Can't open lib" in str(traceback.format_exc()):
				return "lib"

			return False

def saveLog(message):
	log_dir = os.path.expanduser("~") + "/sqlvc/logs/"
	pTime = time.strftime("%m-%d-%Y_%H%M%p")

	if not os.path.isdir(log_dir):
		os.makedirs(log_dir)

	log_obj  = open(log_dir + pTime + ".txt", "w")
	log_obj.write(str(message))
	log_obj.close()


def saveConfigurations(path, connWin = None, mode = 'save'):

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
		#password handler
		#encoded = EncodeDecodePassword(connWin.txtPassword.text(), globalvars.masterPassword, 1)

		if str(connWin.cmbServers.currentText()) not in [elem.attrib["instance"] for elem in root.findall('instances/instance')]:
			ET.SubElement(doc, "instance", 
				instance=str(connWin.cmbServers.currentText()),
				authentication = str(connWin.cmbAuthType.currentText()),
				user = str(connWin.txtUserName.text()),
				password="").text = str(connWin.cmbServers.currentText())

		for instance in root.findall("instances/instance"):
			if instance.attrib["instance"] == str(connWin.cmbServers.currentText()):
				instance.set("selected", "1")
				instance.set("authentication", str(connWin.cmbAuthType.currentText()))
				instance.set("user", str(connWin.txtUserName.text()))
				instance.set("password", ("1" if connWin.chkRemember.isChecked() else "0"))

				#save password to keyring
				if str(connWin.cmbAuthType.currentText()) == "SQL Authentication":
					passKey = str(connWin.txtPassword.text()) if connWin.chkRemember.isChecked() else ""
					password(str(connWin.cmbServers.currentText()), str(connWin.txtUserName.text()), passKey)
			else:
				instance.set("selected", "0")
			#print(instance.attrib["instance"])

	if mode == 'save':
		tree = ET.ElementTree(root)
		tree.write(path)

def password(instance, username, password = None):
	if password is not None:
		keyring.set_password(instance, username, password)
	else:
		return keyring.get_password(instance, username)


def readConnConfiguration(path, connWin = None):
	if os.path.exists(path):
		root = ET.parse(path).getroot()
		instances = root.findall('instances/instance')
		
		cmbIndex = 0

		for instance in reversed(instances):
			connWin.layout.cmbServers.addItem(instance.attrib["instance"])

			if instance.attrib["selected"] == "1":

				#retrieve password from keyring
				txtPassword = ""
				if instance.attrib["authentication"] == "SQL Authentication":
					txtPassword = password(instance.attrib["instance"], instance.attrib["user"])

				serverIndex = connWin.layout.cmbServers.findText(instance.attrib["instance"])
				connWin.layout.cmbServers.setCurrentIndex(serverIndex)

				authIndex = connWin.layout.cmbAuthType.findText(instance.attrib["authentication"])
				connWin.layout.cmbAuthType.setCurrentIndex(authIndex)

				connWin.layout.txtUserName.setText(instance.attrib["user"])
				connWin.layout.txtPassword.setText(txtPassword)

				if instance.attrib["password"] == "1":
					connWin.layout.chkRemember.setChecked(1)
				else:
					connWin.layout.chkRemember.setChecked(0)

			cmbIndex = cmbIndex + 1

	if connWin.layout.cmbServers.currentText() == "":
		connWin.layout.cmbServers.setFocus()
	elif connWin.layout.txtUserName.text() == "":
		connWin.layout.txtUserName.setFocus()
	elif connWin.layout.txtPassword.text() == "":
		connWin.layout.txtPassword.setFocus()
	else:
		connWin.layout.txtPassword.setFocus()

def getUserObject():

	if globalvars.engine == "Microsoft SQL Server":
		conn = pyodbc.connect(globalvars.connString)
		cursor = conn.cursor()
		cursor.execute("select [RowID],[DatabaseName],[SchemaName],[ObjectName],[LoginName],[ObjectType] from [SQLVC].[dbo].[UserWorkspace] where LoginName='" + globalvars.username + "' and SchemaName is not null order by DatabaseName, ObjectType, ObjectName")
		#cursor.execute("select * from [SQLVC].[dbo].[UserWorkspace]")
		rows = cursor.fetchall()

	globalvars.databaseEdits = rows

	conn.close()

	generateView()

# def EncodeDecodePassword(password, master, mode):
# 	passKey = ""
# 	masterHash = SHA256.new(master).hexdigest()[0:32]
	
# 	if mode == 1:
# 		cipher = AES.new(masterHash,AES.MODE_ECB)
# 		passKey = base64.b64encode(cipher.encrypt(password))
	
# 	if mode == 0:
# 		decoded = cipher.decrypt(base64.b64decode(encoded))
# 		passKey = decoded.strip()
# 	print(passKey)
# 	return passKey

def generateView():
	#clearQTreeWidget(globalvars.objListTab) #clean objet list
	globalvars.objListTab.clear()
	trViewObjects = treeModel()
	trViewObjects.generateView(globalvars.objListTab, globalvars.databaseEdits)

# def clearQTreeWidget(tree):
# 	# root = tree.invisibleRootItem()
# 	# for item in tree.selectedItems():
# 	# 	(item.parent() or root).removeChild(item)
# 	item = tree.invisibleRootItem()
# 	for i in range(item.childCount()):
# 		child = item.child(i)
# 		if child.parent() != None:
# 			child.parent().removeChild(child)

def generateObjectScript(user, database, objType, objName, rowId = None):

	viewObj = ""

	if globalvars.engine == "Microsoft SQL Server":
		if rowId == None:
			if objType == 'TABLE':
				query = get_latest_script_v2(user, database, objType[0:1], objName.split(".")[1])
			else:
				query = get_latest_script_by_user(user, database, objType, objName)
		else:
			query = get_latest_script_by_rowid(str(rowId))


		if objType == 'TABLE':
			if globalvars.authType == "Windows Authentication":
				connString = "DRIVER={" + globalvars.SQLSERVER + "};SERVER=" + globalvars.server + ";DATABASE=" + database + ";Trusted_Connection=yes;"
			else:
				connString = "DRIVER={" + globalvars.SQLSERVER + "};SERVER=" + globalvars.server + ";DATABASE=" + database + ";UID=" + globalvars.username + ";PWD=" + globalvars.password
		else:
			connString = globalvars.connString

		conn = pyodbc.connect(connString)
		cursor = conn.cursor()
		cursor.execute(query)
		rows = cursor.fetchall()
		for row in rows:
			viewObj = row[0]

	return viewObj

def generateShelfScript(user, database, objType, objName, rowId = None):

	viewObj = ""

	if globalvars.engine == "Microsoft SQL Server":

		query = get_shelfitem_by_rowid(database, objType, objName, str(rowId))

		if objType == 'TABLE':
			if globalvars.authType == "Windows Authentication":
				connString = "DRIVER={" + globalvars.SQLSERVER + "};SERVER=" + globalvars.server + ";DATABASE=" + database + ";Trusted_Connection=yes;"
			else:
				connString = "DRIVER={" + globalvars.SQLSERVER + "};SERVER=" + globalvars.server + ";DATABASE=" + database + ";UID=" + globalvars.username + ";PWD=" + globalvars.password
		else:
			connString = globalvars.connString

		conn = pyodbc.connect(connString)
		cursor = conn.cursor()
		cursor.execute(query)
		rows = cursor.fetchall()
		for row in rows:
			viewObj = row[0]

	return viewObj

def generateCommitScript(user, database, objType, objName, commitId = ''):
	viewObj = ""

	if globalvars.engine == "Microsoft SQL Server":
		query = get_latest_script_by_commit(database, objType, objName, commitId)
		conn = pyodbc.connect(globalvars.connString)
		cursor = conn.cursor()
		cursor.execute(query)
		rows = cursor.fetchall()
		for row in rows:
			viewObj = row[0]
	return viewObj

def generateShelveScript(user, database, objType, objName, shelveID = ''):
	viewObj = ""

	if globalvars.engine == "Microsoft SQL Server":
		query = get_shelfitem_by_rowid(database, objType, objName, shelveID)
		conn = pyodbc.connect(globalvars.connString)
		cursor = conn.cursor()
		cursor.execute(query)
		rows = cursor.fetchall()
		for row in rows:
			viewObj = row[0]
	return viewObj



def generateRemoteScript(server, auth, serverUser, serverPass, database, objType, objName):
	
	try:
		viewObj = ""
		
		if globalvars.engine == "Microsoft SQL Server":

			if auth == "Windows Authentication":
				connString = "DRIVER={" + globalvars.SQLSERVER + "};SERVER=" + server + ";DATABASE=" + database + ";Trusted_Connection=yes;"
			else:
				connString = "DRIVER={" + globalvars.SQLSERVER + "};SERVER=" + server + ";DATABASE=" + database + ";UID=" + serverUser + ";PWD=" + serverPass

			#query = get_latest_script_by_user('', database, objType, objName)
			#otype = objType[0:1]
			otype = getObjectType(objType.upper())
			oname = objName.split(".")[1]

			query = get_latest_script(otype, oname)
			conn = pyodbc.connect(connString)
			cursor = conn.cursor()
			cursor.execute(query)
			rows = cursor.fetchall()
			for row in rows:
				viewObj = row[0]
		return viewObj

	except Exception as e:
		# saveLog(traceback.format_exc())
		# error_message = "Error fetching remote script. Please see log file"
		# reply = QtWidgets.QMessageBox.question(globalvars.MainWindow, "Apply Merged", error_message,  QtWidgets.QMessageBox.Ok)

		err_msg = str(traceback.format_exc())
		saveLog(err_msg)

		if "Cannot open database" in err_msg:
			error_message = "Access denied, database does not exist. Check server or map to destination database. See log file for more info."
			reply = QtWidgets.QMessageBox.question(globalvars.MainWindow, "Error Applying Merge", error_message,  QtWidgets.QMessageBox.Ok)

			return "ERROR GENERATING SCRIPT, SEE LOG FILE!!!"

def getObjectType(objectTypeName):
	objects = globalvars.objectDefinition

	try:
		return objects[objectTypeName]
	except Exception as e:
		saveLog(traceback.format_exc())
		return objectTypeName[0:1]


def generateVersionList(database, objType, objName):

	viewObj = []

	if globalvars.engine == "Microsoft SQL Server":
		query = get_script_by_versions(database, objType, objName)
		conn = pyodbc.connect(globalvars.connString)
		cursor = conn.cursor()
		cursor.execute(query)
		viewObj = cursor.fetchall()

	return viewObj

def generateCommitListPerItem(database, objType, objName):

	viewObj = []

	if globalvars.engine == "Microsoft SQL Server":
		query =get_script_by_commit_per_item(database,objType,objName)

		conn = pyodbc.connect(globalvars.connString)
		cursor = conn.cursor()
		cursor.execute(query)
		viewObj = cursor.fetchall()


	return viewObj


def downloadToCompare(user, db1, objType1, objName1, db2, objType2, objName2, compareType, rowId1 = '', rowId2 = '', server1 = '', server2 = '', serverUser1 = '', serverUser2 = '', serverPass1 = '', serverPass2 = '', auth1 = '', auth2 = ''):
	compare_directory = str(tempfile.gettempdir()) + "/slvc_tmp/"
	obj1 = ""
	obj2 = ""
	name1 = ""
	name2 = ""
	name_preserve = ""
	overwrite = True
	targetDB = ""
	hash_md5 = hashlib.md5()
	hexdigest = ""
	#added subdirectory 
	if not os.path.isdir(compare_directory):
		os.makedirs(compare_directory)

	if globalvars.engine == "Microsoft SQL Server":
		if compareType == "compareLatest": #compare your edits to currently applied
			name1 = compare_directory + objName1 + "_LATEST.sql"
			name2 = compare_directory + objName2 + "_LATEST_USERVERSION.sql"
			obj1 = generateObjectScript('', db1, objType1, objName1) #latest version of the script
			obj2 = generateObjectScript(user, db2, objType2, objName2) #latest version of the user
			# hash_md5.update(obj2.encode("utf-8"))
			# hexdigest = hash_md5.hexdigest()
			targetDB = db2
			name_preserve = objName2 + "_LATEST_USERVERSION.sql"

		elif compareType == "compareversion": #compare your edits to other versions
			name1 = compare_directory + objName1 + "_HISTORY("+str(rowId1)+").sql"
			name2 = compare_directory + objName2 + "_LATEST_USERVERSION.sql"

			obj1 = generateObjectScript('', '', '', '', rowId1) #latest version of the script
			obj2 = generateObjectScript(user, db2, objType2, objName2) #latest version of the user

			targetDB = db2
			name_preserve = objName2 + "_LATEST_USERVERSION.sql"

		elif compareType == "comparecommit": #compare your edits to other commit
			name1 = compare_directory + objName1 + "_COMMIT("+str(rowId1)+").sql"
			name2 = compare_directory + objName2 + "_LATEST_USERVERSION.sql"

			obj1 = generateCommitScript(user, db1, objType1, objName1, rowId1) #latest version of the script
			obj2 = generateObjectScript(user, db2, objType2, objName2) #latest version of the user
			targetDB = db2
			name_preserve = objName2 + "_LATEST_USERVERSION.sql"

		elif compareType == "comparecommit2":
			name1 = compare_directory + objName1 + "_COMMIT("+str(rowId1)+").sql"
			name2 = compare_directory + objName2 + "_COMMIT("+str(rowId2)+").sql"

			obj1 = generateCommitScript(user, db1, objType1, objName1, rowId1) #latest version of the script
			obj2 = generateCommitScript(user, db2, objType2, objName2, rowId2) #latest version of the script

			targetDB = db2
			name_preserve = objName2 + "_COMMIT("+str(rowId2)+").sql"

		elif compareType == "compareToServer":
			name1 = compare_directory + objName1 + "_COMMIT("+str(rowId1)+").sql"
			name2 = compare_directory + objName2 + "_SERVER("+str(server2.replace("\\","-"))+").sql"

			obj1 = generateCommitScript(user, db1, objType1, objName1, rowId1)
			obj2 = generateRemoteScript(server2, auth2, serverUser2, serverPass2, db2, objType2, objName2)
			
			targetDB = db2
			name_preserve = objName2 + "_SERVER("+str(server2.replace("\\","-"))+").sql"

		elif compareType == "compareShelfLatest":
			name1 = compare_directory + objName1 + "_LATEST.sql"
			name2 = compare_directory + objName2 + "_SHELF("+str(rowId1)+").sql"

			obj1 = generateShelfScript(user, db1, objType1, objName1, rowId1)
			obj2 = generateObjectScript('', db1, objType1, objName1) #latest version of the script

			targetDB = db2
			name_preserve = objName2 + "_SHELF("+str(rowId2)+").sql"

	c1 = open(name1, "w")
	c1.write(obj1.replace("\r\n","\n"))
	c1.close()

	#added in case of error or user decided to re-open merged file instead
	if os.path.exists(name2):
		msgBox = QtWidgets.QMessageBox()
		msgBox.setText('A merged file for '+name_preserve+' has been preserved. What would you like to do?')
		msgBox.addButton(QtWidgets.QPushButton('Overwrite'), QtWidgets.QMessageBox.YesRole)
		msgBox.addButton(QtWidgets.QPushButton('Re-open file'), QtWidgets.QMessageBox.NoRole)
		msgBox.addButton(QtWidgets.QPushButton('Cancel'), QtWidgets.QMessageBox.RejectRole)
		reply = msgBox.exec_()

		if reply == 1:
			overwrite = False

	if overwrite:
		c2 = open(name2, "w")
		c2.write(obj2.replace("\r\n","\n"))
		c2.close()

	#read again..bug for windows...hashes are not same
	beforeEdit = open(name2, "rb")
	beforeEditText = beforeEdit.read()
	beforeEdit.close()

	#create hash
	hash_md5.update(beforeEditText)
	hexdigest = hash_md5.hexdigest()

	exePath = globalvars.sett.layout.readExePath()

	if exePath != None and len(exePath) > 0:
		delete = True
		p = subprocess.Popen([exePath, name1, name2], stdin=subprocess.PIPE, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
		output, err = p.communicate(b"input data that is passed to subprocess' stdin")
		rc = p.returncode
		
		if rc == 0 and compareType != 'comparecommit2': #apply changes if not compare to other commit
			
			new_hash_md5 = hashlib.md5()
			
			merged = open(name2, "rb")
			toApply = merged.read()
			merged.close()

			new_hash_md5.update(toApply)

			#check there are changes in script file
			#added option to re-check file application if re-opened un-applied merged file
			if hexdigest != new_hash_md5.hexdigest() or overwrite == False:

				# apply_message = "Apply merged files? You cannot push your code unless you owned the latest version."
				# reply  = QtWidgets.QMessageBox.question(globalvars.MainWindow, "Install Scripts", apply_message,  QtWidgets.QMessageBox.Ok,  QtWidgets.QMessageBox.Cancel)

				msgBox = QtWidgets.QMessageBox()
				msgBox.setText('Apply merged files? You cannot push your code unless you owned the latest version.')
				msgBox.addButton(QtWidgets.QPushButton('Apply merge'), QtWidgets.QMessageBox.YesRole)
				msgBox.addButton(QtWidgets.QPushButton('Preserve merge, I\'ll comeback later'), QtWidgets.QMessageBox.NoRole)
				msgBox.addButton(QtWidgets.QPushButton('Discard changes and exit'), QtWidgets.QMessageBox.RejectRole)
				reply = msgBox.exec_()

				
				if reply == 0:
					
					if compareType == 'compareToServer':
						checkForApply(toApply, targetDB, auth2, server2, serverUser2, serverPass2, objType2)
					else:
						#fix authentication error
						if auth1 == '':
							auth1 = globalvars.authType

						checkForApply(toApply, targetDB, auth1, '', '', '', objType2)

				if reply == 1:
					delete = False

				# if name1 != "":
				# 	os.remove(name1)

				# if name2 != "":
				# 	os.remove(name2)

			if compareType == "compareversion":
				globalvars.compareObj.show()
				globalvars.compareObj.setWindowFlags(globalvars.compareObj.windowFlags() | QtCore.Qt.WindowStaysOnTopHint)
		
		if delete:
			if name1 != "":
				os.remove(name1)

			if name2 != "":
				os.remove(name2)
	else:
		apply_message = "No difftool found. Please define one in Edit > Preferences > Difftool"
		reply  = QtWidgets.QMessageBox.question(globalvars.MainWindow, "Install Scripts", apply_message,  QtWidgets.QMessageBox.Ok,  QtWidgets.QMessageBox.Cancel)


def checkForApply(mergedFile, targetDB,targetAuth = '', targetServer = '', targetUser = '', targetPass = '', targetType = ''):
	try:
		if globalvars.engine == "Microsoft SQL Server":

			if targetServer == '':
				server =  globalvars.server
			else:
				server = targetServer

			if targetUser == '':
				user = globalvars.username
			else:
				user = targetUser

			if targetPass == '':
				password = globalvars.password
			else:
				password = targetPass

			if targetAuth == "Windows Authentication":
				connString = "DRIVER={" + globalvars.SQLSERVER + "};SERVER=" + server + ";DATABASE=" + targetDB + ";Trusted_Connection=yes;"
			else:
				connString = "DRIVER={" + globalvars.SQLSERVER + "};SERVER=" + server + ";DATABASE=" + targetDB + ";UID=" + user + ";PWD=" + password
			
			conn = pyodbc.connect(connString, autocommit=True)
			cursor = conn.cursor()

			if targetType == 'TABLE':
				print("table")
			else:
				cursor.execute(mergedFile.decode('UTF-8'))

			message = "Successfully applied script"
			reply = QtWidgets.QMessageBox.question(globalvars.MainWindow, "Apply Merged", message,  QtWidgets.QMessageBox.Ok)

	except Exception as e:
		saveLog(traceback.format_exc())
		error_message = "Error applying merged file. Please see log file"
		reply = QtWidgets.QMessageBox.question(globalvars.MainWindow, "Apply Merged", error_message,  QtWidgets.QMessageBox.Ok)

def commitToOtherServer(commitPanel):
	try:
		selected_items, missing_item_names = select_remote_item(commitPanel)
		
		if len(selected_items) == 0:
			commit_message = "No item selected to commit."
			reply = QtWidgets.QMessageBox.question(globalvars.MainWindow, "Commit Changes", commit_message,  QtWidgets.QMessageBox.Ok)
		else:
			commit_message = "You are about to commit changes in database. Continue?"
			reply = QtWidgets.QMessageBox.question(globalvars.MainWindow, "Commit Changes", commit_message,  QtWidgets.QMessageBox.Ok, QtWidgets.QMessageBox.Cancel)
			conflicts = []
			globalvars.MainWindow.conflictList.clear()

			if reply == QtWidgets.QMessageBox.Ok:

				if globalvars.engine == "Microsoft SQL Server":
					rowId = ",".join(selected_items)
					query = """select case when (select top 1 LoginName from [dbo].[DDLEvents] 
								where DatabaseName=ws.DatabaseName and SchemaName=ws.SchemaName and ObjectType=ws.ObjectType and ObjectName=ws.ObjectName 
								order by RowID desc) = ws.LoginName 
								then 'ok' else 'conflict' end,*
								from [dbo].[UserWorkspace] ws where RowId in (""" + rowId + """)"""
					
					conn = pyodbc.connect(commitPanel.connString)
					cursor = conn.cursor()
					rows = cursor.execute(query)

					for row in rows:
						if row[0] == 'conflict':
							conflicts.append(row)

					if len(conflicts) > 0 or len(missing_item_names) > 0 : #conflict detected
						commit_message = "Conflicting items detected. Kindly review."
						reply = QtWidgets.QMessageBox.question(globalvars.MainWindow, "Commit Changes", commit_message,  QtWidgets.QMessageBox.Ok)
						globalvars.MainWindow.showConflictTab()

						for conflict in conflicts:
							citem =  QtWidgets.QListWidgetItem(conflict[4] + " latest version is not owned by you")
							globalvars.MainWindow.conflictList.addItem(citem)

						for missing in missing_item_names:
							citem =  QtWidgets.QListWidgetItem(missing + " is not yet applied")
							globalvars.MainWindow.conflictList.addItem(citem)

					else:
						#check if commit message is empty
						text = str(commitPanel.txtCommitMessage.toPlainText())
						if text.strip()  == "":
							commit_message = "Empty commit message"
							reply = QtWidgets.QMessageBox.question(globalvars.MainWindow, "Commit Changes", commit_message,  QtWidgets.QMessageBox.Ok)
							globalvars.MainWindow.commitMessage.setFocus()
						else:
							commitID = ""

							if globalvars.engine == "Microsoft SQL Server":

								commitID = commitPanel.serverMerge.replace("\\","-")

								rowId = ",".join(selected_items)

								query1 = """insert into [SQLVC].[dbo].[Commits_hdr](CommitID, LoginName, CommitMessage, ChangesetDate)
												values('""" + commitID + """','""" + commitPanel.usernameMerge + """','""" + text + """',GETDATE())"""

								query1_1 = "select @@IDENTITY"

								conn = pyodbc.connect(commitPanel.connString, autocommit=True)

								cursor = conn.cursor()
								cursor.execute(query1)
								ident = cursor.execute(query1_1)

								for i in ident:
									commitID = commitID + "-" + str(i[0])


								query2 = save_commit_detail(commitID, rowId)

								print("commiting items")
								cursor.execute(query2)

								query_delete = """delete from [SQLVC].[dbo].[UserWorkspace] where RowId in (""" + rowId + """);"""

								print("deleting commited item in workspace")
								cursor.execute(query_delete)

								conn.close()


							commit_message = "Changes has been commited. Commit ID " + commitID + " has been created."
							reply = QtWidgets.QMessageBox.question(globalvars.MainWindow, "Commit Changes", commit_message,  QtWidgets.QMessageBox.Ok)
							globalvars.MainWindow.commitMessage.document().setPlainText("")
							#remove items
							getUserObject()
							getChangesets()

	except Exception as e:
		saveLog(traceback.format_exc())
		error_message = "Error commiting file to remote server. Please see log file for error."
		reply = QtWidgets.QMessageBox.question(globalvars.MainWindow, "Commit Changes", error_message,  QtWidgets.QMessageBox.Ok)

def CommitChanges(MainWindow, flag=''):
	try:
		treeView = MainWindow.objListTab
		# treeView.setSelectionMode(QtWidgets.QAbstractItemView.ContiguousSelection)
		# treeView.selectAll()
		# print(treeView.selectedIndexes())
		item = treeView.invisibleRootItem()
		selected_items = select_item(item)
		
		if len(selected_items) == 0:
			commit_message = "No item selected to commit."
			reply = QtWidgets.QMessageBox.question(globalvars.MainWindow, "Commit Changes", commit_message,  QtWidgets.QMessageBox.Ok)
		else:
			commit_message = "You are about to commit changes in database. Continue?"
			reply = QtWidgets.QMessageBox.question(globalvars.MainWindow, "Commit Changes", commit_message,  QtWidgets.QMessageBox.Ok, QtWidgets.QMessageBox.Cancel)
			conflicts = []
			globalvars.MainWindow.conflictList.clear()

			if reply == QtWidgets.QMessageBox.Ok:

				if globalvars.engine == "Microsoft SQL Server":
					rowId = ",".join(selected_items)
					query = checkConflict(rowId)
					
					conn = pyodbc.connect(globalvars.connString)
					#print(query)
					cursor = conn.cursor()
					rows = cursor.execute(query)

					for row in rows:
						if row[0] == 'conflict':
							conflicts.append(row) 
				#check for conflicts
				#initialize conflict list
				globalvars.MainWindow.conflictList.clear()
				if len(conflicts) > 0: #conflict detected
					commit_message = "Conflicting items detected. Kindly review."
					reply = QtWidgets.QMessageBox.question(globalvars.MainWindow, "Commit Changes", commit_message,  QtWidgets.QMessageBox.Ok)
					globalvars.MainWindow.showConflictTab()

					for conflict in conflicts:
						citem =  QtWidgets.QListWidgetItem(conflict[4])
						globalvars.MainWindow.conflictList.addItem(citem)

				else:
					#check if commit message is empty
					text = str(globalvars.MainWindow.commitMessage.toPlainText())
					if text.strip()  == "":
						commit_message = "Empty commit message"
						reply = QtWidgets.QMessageBox.question(globalvars.MainWindow, "Commit Changes", commit_message,  QtWidgets.QMessageBox.Ok)
						globalvars.MainWindow.commitMessage.setFocus()
					else:
						commitID = ""

						if globalvars.engine == "Microsoft SQL Server":

							commitID = globalvars.server.replace("\\","-")

							rowId = ",".join(selected_items)

							query1 = """insert into [SQLVC].[dbo].[Commits_hdr](CommitID, LoginName, CommitMessage, ChangesetDate)
											values('""" + commitID + """','""" + globalvars.username + """','""" + text + """',GETDATE())"""

							query1_1 = "select @@IDENTITY"

							conn = pyodbc.connect(globalvars.connString, autocommit=True)

							cursor = conn.cursor()
							cursor.execute(query1)
							ident = cursor.execute(query1_1)

							for i in ident:
								commitID = commitID + "-" + str(i[0])


							query2 = save_commit_detail(commitID, rowId)


							print("commiting items")
							cursor.execute(query2)

							query_delete = """delete from [SQLVC].[dbo].[UserWorkspace] where RowId in (""" + rowId + """);"""
							
							print("deleting commited item in workspace")
							cursor.execute(query_delete)

							conn.close()


						commit_message = "Changes has been commited. Commit ID " + commitID + " has been created."
						reply = QtWidgets.QMessageBox.question(globalvars.MainWindow, "Commit Changes", commit_message,  QtWidgets.QMessageBox.Ok)
						globalvars.MainWindow.commitMessage.document().setPlainText("")
						#remove items
						getUserObject()
						getChangesets()

	except Exception as e:
		saveLog(traceback.format_exc())
		error_message = "Error commiting file. Please see log file for error."
		reply = QtWidgets.QMessageBox.question(globalvars.MainWindow, "Commit Changes", error_message,  QtWidgets.QMessageBox.Ok)

def ShelveChanges(MainWindow, flag=''):
	try:
		treeView = MainWindow.objListTab
		item = treeView.invisibleRootItem()
		selected_items = select_item(item)
		
		if len(selected_items) == 0:
			shelve_message = "No item selected to shelve."
			reply = QtWidgets.QMessageBox.question(globalvars.MainWindow, "Commit Changes", shelve_message,  QtWidgets.QMessageBox.Ok)
		else:
			shelve_message = "You are about to shelve changes in database. Continue?"
			reply = QtWidgets.QMessageBox.question(globalvars.MainWindow, "Commit Changes", shelve_message,  QtWidgets.QMessageBox.Ok, QtWidgets.QMessageBox.Cancel)
			conflicts = []

			if reply == QtWidgets.QMessageBox.Ok:
				#check if commit message is empty
				text = str(globalvars.MainWindow.commitMessage.toPlainText())
				if text.strip()  == "":
					shelve_message = "Empty shelve message"
					reply = QtWidgets.QMessageBox.question(globalvars.MainWindow, "Commit Changes", shelve_message,  QtWidgets.QMessageBox.Ok)
					globalvars.MainWindow.commitMessage.setFocus()
				else:
					commitID = ""

					if globalvars.engine == "Microsoft SQL Server":

						shelveID = "shelve-" + globalvars.server.replace("\\","-")

						rowId = ",".join(selected_items)

						query1 = """insert into [SQLVC].[dbo].[Shelve_hdr](ShelveID, LoginName, ShelveMessage, ShelveDate)
										values('""" + shelveID + """','""" + globalvars.username + """','""" + text + """',GETDATE())"""

						query1_1 = "select @@IDENTITY"

						conn = pyodbc.connect(globalvars.connString, autocommit=True)

						cursor = conn.cursor()
						cursor.execute(query1)
						ident = cursor.execute(query1_1)

						for i in ident:
							shelveID = shelveID + "-" + str(i[0])


						query2 = save_shelve_detail(shelveID, rowId)


						print("shelving items")
						cursor.execute(query2)

						query_delete = """delete from [SQLVC].[dbo].[UserWorkspace] where RowId in (""" + rowId + """);"""
						
						print("deleting shelved item in workspace")
						cursor.execute(query_delete)

						conn.close()


					shelve_message = "Object has been shelved. Shelve ID " + shelveID + " has been created."
					reply = QtWidgets.QMessageBox.question(globalvars.MainWindow, "Commit Changes", shelve_message,  QtWidgets.QMessageBox.Ok)
					globalvars.MainWindow.commitMessage.document().setPlainText("")
					#remove items
					getUserObject()
					getChangesets()
					getShelve()

	except Exception as e:
		saveLog(traceback.format_exc())
		error_message = "Error commiting file. Please see log file for error."
		reply = QtWidgets.QMessageBox.question(globalvars.MainWindow, "Commit Changes", error_message,  QtWidgets.QMessageBox.Ok)


def getChangesets():
	globalvars.MainWindow.lstCommitsModel.removeRows(0,  globalvars.MainWindow.lstCommitsModel.rowCount())
	if globalvars.engine == "Microsoft SQL Server":
		conn = pyodbc.connect(globalvars.connString, autocommit=True)
		cursor = conn.cursor()
		commits = cursor.execute("select RowId, CommitID, CommitMessage,LoginName,ChangesetDate  from [SQLVC].[dbo].[Commits_hdr] order by RowId asc")

	for commit in commits:
		# citem =  QtWidgets.QListWidgetItem(str(commit[1]) + "-" + str(commit[0]))
		# globalvars.MainWindow.lstCommits.addItem(citem)
		commitID = str(commit[1]) + "-" + str(commit[0])
		user = str(commit[3])
		commitMessaage = str(commit[2])
		date = str(commit[4])

		globalvars.MainWindow.addCommit(globalvars.MainWindow.lstCommitsModel, commitID, user, commitMessaage,date)


def getShelve():
	globalvars.MainWindow.lstShelveModel.removeRows(0,  globalvars.MainWindow.lstShelveModel.rowCount())
	if globalvars.engine == "Microsoft SQL Server":
		conn = pyodbc.connect(globalvars.connString, autocommit=True)
		cursor = conn.cursor()
		shelves = cursor.execute("select RowId, ShelveID, ShelveMessage,LoginName,ShelveDate  from [SQLVC].[dbo].[shelve_hdr] order by RowId asc")

	for shelve in shelves:
		shelveID = str(shelve[1]) + "-" + str(shelve[0])
		user = str(shelve[3])
		shelveMessaage = str(shelve[2])
		date = str(shelve[4])

		globalvars.MainWindow.addShelve(globalvars.MainWindow.lstShelveModel, shelveID, user, shelveMessaage,date)

def removeItemToWorkspace(rowId):
	try:

		message = "Continue removing item? This cannot be undone."
		reply = QtWidgets.QMessageBox.question(globalvars.MainWindow, "Remove Item", message,  QtWidgets.QMessageBox.Ok, QtWidgets.QMessageBox.Cancel)

		if reply == QtWidgets.QMessageBox.Ok:
			if globalvars.engine == "Microsoft SQL Server":
				query = "delete from [SQLVC].[dbo].[UserWorkspace] where RowID in (" + str(rowId) + ")"
				conn = pyodbc.connect(globalvars.connString, autocommit=True)
				cursor = conn.cursor()
				commits = cursor.execute(query)

			message = "Successfully removed item."
			reply = QtWidgets.QMessageBox.question(globalvars.MainWindow, "Remove Item", message,  QtWidgets.QMessageBox.Ok)
			getUserObject()

	except Exception as e:
		saveLog(traceback.format_exc())
		error_message = "Error removing item. Please see log file for details."
		reply = QtWidgets.QMessageBox.question(globalvars.MainWindow, "Remove Item", error_message,  QtWidgets.QMessageBox.Ok)



# def clearQTreeWidget(tree, model):
# 	model.removeRows(0, model.rowCount())
	# iterator = QtGui.QTreeWidgetItemIterator(tree, QtGui.QTreeWidgetItemIterator.All)
	# while iterator.value():
	# 	iterator.value().takeChildren()
	# 	iterator +=1
	# 	i = tree.topLevelItemCount()
	# while i > -1:
	# 	treeWidget.takeTopLevelItem(i)
	# 	i -= 1

def select_item(item, mode = 0):
	# mode 1 = delete
	selected_item = []

	for i in range(item.childCount()):

		child1 = item.child(i)

		for j in range(child1.childCount()):

			child2 = child1.child(j)

			for k in range(child2.childCount()):

				child3 = child2.child(k)

				for l in range(child3.childCount()):
					
					child4 = child3.child(l)

					if child4.checkState(0) == QtCore.Qt.Checked:
						
						if mode == 0:
							rowId = child4.data(QtCore.Qt.UserRole,0)

							selected_item.append(str(rowId))

						if mode == 1:
							child4.parent().removeChild(child4)

	return selected_item

def select_remote_item(commitWin):

	item = commitWin.commitList.invisibleRootItem()

	selected_item = []
	missingitem_names = []

	for i in range(item.childCount()):

		child1 = item.child(i)

		for j in range(child1.childCount()):

			child2 = child1.child(j)

			for k in range(child2.childCount()):

				child3 = child2.child(k)

				for l in range(child3.childCount()):
					
					child4 = child3.child(l)

					if child4.checkState(0) == QtCore.Qt.Checked:

						itemText = child4.text(0)

						dbObjType = child4.parent()
						dbObjTypeText = dbObjType.text(0)

						database = dbObjType.parent()
						databaseText = database.text(0)

						rowid = get_remote_rowid(commitWin.connString, commitWin.usernameMerge, databaseText, dbObjTypeText, itemText)
						selected_item.append(str(rowid))

						if rowid == 0:
							missingitem_names.append(itemText)



	return selected_item, missingitem_names

def get_remote_rowid(connString, user, database, objType, objectName):
	try:
		if globalvars.engine == "Microsoft SQL Server":
			rowid = 0

			query = get_workspace_script_by_user(user, database, objType, objectName)
			conn = pyodbc.connect(connString, autocommit=True)
			cursor = conn.cursor()
			data = cursor.execute(query)
			for row in data:
				rowid = row[0]
			
			return rowid


	except Exception as e:
		saveLog(traceback.format_exc())
		error_message = "Error getting commit details. Please see log file for details."
		reply = QtWidgets.QMessageBox.question(globalvars.MainWindow, "Remove Item", error_message,  QtWidgets.QMessageBox.Ok)

def getCommitDetails(commitid):
	try:
		if globalvars.engine == "Microsoft SQL Server":
			query = "select RowID, DatabaseName, SchemaName, ObjectName, LoginName, ObjectType from [SQLVC].[dbo].[Commits_dtl] where CommitID='" + commitid + "' order by DatabaseName, ObjectType, ObjectName"
			conn = pyodbc.connect(globalvars.connString, autocommit=True)
			cursor = conn.cursor()
			data = cursor.execute(query)
			return data


	except Exception as e:
		saveLog(traceback.format_exc())
		error_message = "Error getting commit details. Please see log file for details."
		reply = QtWidgets.QMessageBox.question(globalvars.MainWindow, "Commits", error_message,  QtWidgets.QMessageBox.Ok)


def getSheveDetails(shelveid, userid):
	try:
		if globalvars.engine == "Microsoft SQL Server":
			query = getShelvedDetails(shelveid, userid)
			conn = pyodbc.connect(globalvars.connString, autocommit=True)
			cursor = conn.cursor()
			data = cursor.execute(query)
			return data

	except Exception as e:
		saveLog(traceback.format_exc())
		error_message = "Error getting shelf details. Please see log file for details."
		reply = QtWidgets.QMessageBox.question(globalvars.MainWindow, "Shelf", error_message,  QtWidgets.QMessageBox.Ok)

def encode(key, clear):
    enc = []
    for i in range(len(clear)):
        key_c = key[i % len(key)]
        enc_c = chr((ord(clear[i]) + ord(key_c)) % 256)
        enc.append(enc_c)
    return base64.urlsafe_b64encode("".join(enc).encode()).decode()

def decode(key, enc):
    dec = []
    enc = base64.urlsafe_b64decode(enc).decode()
    for i in range(len(enc)):
        key_c = key[i % len(key)]
        dec_c = chr((256 + ord(enc[i]) - ord(key_c)) % 256)
        dec.append(dec_c)
    return "".join(dec)


def getCompiledScripts(id):
	try:
		if globalvars.engine == "Microsoft SQL Server":
			query = """SELECT [EventDDL] FROM [SQLVC].[dbo].[DDLEvents] where RowID in ("""+id+""") order by RowID asc"""
			conn = pyodbc.connect(globalvars.connString, autocommit=True)
			cursor = conn.cursor()
			data = cursor.execute(query)
			return data


	except Exception as e:
		saveLog(traceback.format_exc())
		error_message = "Error compiling scripts. Please see log file for details."
		reply = QtWidgets.QMessageBox.question(globalvars.MainWindow, "Remove Item", error_message,  QtWidgets.QMessageBox.Ok)


def openLogFolder(path):
	#home = expanduser("~")
	#path = home + "/sqlvc/logs"

	if platform.system() == "Windows":
		os.startfile(path)
	elif platform.system() == "Darwin":
		subprocess.Popen(["open", path])
	else:
		subprocess.Popen(["xdg-open", path])

def getDatabaseList(serverType, server, authType, username, password):
	try:
		if globalvars.engine == "Microsoft SQL Server":

			if authType == "Windows Authentication":
				connString = "DRIVER={" + globalvars.SQLSERVER + "};SERVER=" + server + ";DATABASE=master;Trusted_Connection=yes;"
			else:
				connString = "DRIVER={" + globalvars.SQLSERVER + "};SERVER=" + server + ";DATABASE=master;UID=" + username + ";PWD=" + password

			query = getDatabases()
			conn = pyodbc.connect(connString, autocommit=True)
			cursor = conn.cursor()
			data = cursor.execute(query)
			return data


	except Exception as e:
		saveLog(traceback.format_exc())
		error_message = "Getting database list. Please see log file for details."
		reply = QtWidgets.QMessageBox.question(globalvars.MainWindow, "Database List", error_message,  QtWidgets.QMessageBox.Ok)







	




