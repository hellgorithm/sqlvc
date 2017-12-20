import globalvars
import os
import xml.etree.cElementTree as ET
from PyQt5 import QtWidgets, QtGui, QtCore
import pyodbc
import time
from treeModel import treeModel
import tempfile
import subprocess, threading
# import hashlib
# from Crypto.Cipher import AES
# from Crypto.Hash import SHA256
# import base64
import uuid


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
			getChangesets()

		connectWindow.btnCancel.click()
	else:
		error_message = "Could not connect to database server!"
		QtWidgets.QMessageBox.about(connectWindow, "Error", error_message)

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
				instance.set("password", "")
			else:
				instance.set("selected", "0")
			#print(instance.attrib["instance"])

	tree = ET.ElementTree(root)
	tree.write(path)

def readConnConfiguration(path, connWin = None):
	if os.path.exists(path):
		root = ET.parse(path).getroot()
		instances = root.findall('instances/instance')
		
		cmbIndex = 0

		for instance in reversed(instances):
			connWin.layout.cmbServers.addItem(instance.attrib["instance"])

			if instance.attrib["selected"] == "1":

				serverIndex = connWin.layout.cmbServers.findText(instance.attrib["instance"])
				connWin.layout.cmbServers.setCurrentIndex(serverIndex)

				authIndex = connWin.layout.cmbAuthType.findText(instance.attrib["authentication"])
				connWin.layout.cmbAuthType.setCurrentIndex(authIndex)

				connWin.layout.txtUserName.setText(instance.attrib["user"])
				connWin.layout.txtPassword.setText("")

			cmbIndex = cmbIndex + 1

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
	obj1 = ""
	obj2 = ""
	name1 = ""
	name2 = ""
	targetDB = ""
	# hash_md5 = hashlib.md5()
	# hexdigest = ""

	if globalvars.engine == "Microsoft SQL Server":
		if compareType == "compareLatest": #compare your edits to currently applied
			name1 = compare_directory + objName1 + "_LATEST.sql"
			name2 = compare_directory + objName2 + "_LATEST_USERVERSION.sql"
			obj1 = generateObjectScript('', db1, objType1, objName1) #latest version of the script
			obj2 = generateObjectScript(user, db2, objType2, objName2) #latest version of the user
			# hash_md5.update(obj2.encode("utf-8"))
			# hexdigest = hash_md5.hexdigest()
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
			
			#new_hash_md5 = hashlib.md5()
			
			merged = open(name2, "rb")
			toApply = merged.read()
			merged.close()

			#new_hash_md5.update(toApply.encode("utf-8"))

			#check there are changes in script file
			#if hexdigest != new_hash_md5.hexdigest():

			apply_message = "Apply merged files? You cannot push your code unless you owned the lates version."
			reply  = QtWidgets.QMessageBox.question(globalvars.MainWindow, "Install Scripts", apply_message,  QtWidgets.QMessageBox.Ok,  QtWidgets.QMessageBox.Cancel)

			if reply == QtWidgets.QMessageBox.Ok:
				checkForApply(toApply,targetDB)

			if name1 != "":
				os.remove(name1)

			if name2 != "":
				os.remove(name2)

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

def CommitChanges(MainWindow):
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

		if reply == QtWidgets.QMessageBox.Ok:

			if globalvars.engine == "Microsoft SQL Server":
				rowId = ",".join(selected_items)
				query = """select case when (select top 1 LoginName from [dbo].[DDLEvents] 
							where DatabaseName=ws.DatabaseName and SchemaName=ws.SchemaName and ObjectType=ws.ObjectType and ObjectName=ws.ObjectName 
							order by RowID desc) = ws.LoginName 
							then 'ok' else 'conflict' end,*
							from [dbo].[UserWorkspace] ws where RowId in (""" + rowId + """)"""
				
				conn = pyodbc.connect(globalvars.connString)
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


						query2 = """insert into [SQLVC].[dbo].[Commits_dtl](CommitID, DatabaseName, SchemaName, ObjectName, LoginName, ObjectType, ObjectDDL)
							select '""" + commitID + """',DatabaseName, SchemaName, ObjectName, LoginName, ObjectType,(select top 1 EventDDL from [dbo].[DDLEvents] 
							where DatabaseName=ws.DatabaseName and SchemaName=ws.SchemaName and ObjectType=ws.ObjectType and ObjectName=ws.ObjectName 
							order by RowID desc) from [SQLVC].[dbo].[UserWorkspace] ws where RowId in (""" + rowId + """);"""

						cursor.execute(query2)
						#add delete from workspace here

						conn.close()


					commit_message = "Changes has been commited. Commit ID " + commitID + " has been created."
					reply = QtWidgets.QMessageBox.question(globalvars.MainWindow, "Commit Changes", commit_message,  QtWidgets.QMessageBox.Ok)
					globalvars.MainWindow.commitMessage.document().setPlainText("")
					#remove items
					getUserObject()

def getChangesets():
	#globalvars.MainWindow.lstCommits.clear()
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







	




