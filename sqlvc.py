import globalvars
import sys, os, getpass, platform
from PyQt5 import QtWidgets, QtGui, QtCore
import xml.etree.cElementTree as ET
from treeModel import treeModel
from functions import *
from os.path import expanduser
import decimal

#window
from comparewindow import *
from settingswindow import *
from connectwindow import *
from queries import *

import traceback

class MainWindow(QtWidgets.QMainWindow):
	def __init__(self, parent=None):
		super(MainWindow,self).__init__()

		#initialize window
		self.layout = Layout(parent=self)
		self.setWindowTitle("SQLVC " + globalvars.version)
		self.setWindowIcon(QtGui.QIcon('./openmonitor.png'))
		self.setCentralWidget(self.layout)
		self.resize(700, 600)
		#self.setGeometry(10, 10, 700, 600)
		self.center()
		# filling up a menu bar
		bar = self.menuBar()

		# File menu
		file_menu = bar.addMenu('&File')
		edit_menu = bar.addMenu('&Edit')
		help_menu = bar.addMenu('&Help')

		#Open connection
		open_action = QtWidgets.QAction('&Open Connection', self)
		file_menu.addAction(open_action)
		open_action.triggered.connect(self.addConnection)
		open_action.setShortcut(QtGui.QKeySequence("Ctrl+O"))


		refresh_action = QtWidgets.QAction('&Refresh', self)
		file_menu.addAction(refresh_action)
		refresh_action.triggered.connect(self.refreshConn)
		refresh_action.setShortcut(QtGui.QKeySequence("Ctrl+R"))

		open_log = QtWidgets.QAction('Open &Logs', self)
		file_menu.addAction(open_log)
		open_log.triggered.connect(self.openLogFolder)
		open_log.setShortcut(QtGui.QKeySequence("Ctrl+L"))

		preference_action = QtWidgets.QAction('&Preferences', self)
		edit_menu.addAction(preference_action)
		preference_action.triggered.connect(self.openPreference)
		preference_action.setShortcut(QtGui.QKeySequence("Ctrl+P"))

		# dark_action = QtWidgets.QAction('&Dark Mode', self)
		# edit_menu.addAction(dark_action)
		# dark_action.triggered.connect(lambda:self.setDarkMode(self))
		# dark_action.setShortcut(QtGui.QKeySequence("Ctrl+D"))

		close_action = QtWidgets.QAction('&Quit', self)
		file_menu.addAction(close_action)
		close_action.setShortcut(QtGui.QKeySequence("Ctrl+Q"))

		about_action = QtWidgets.QAction('&About', self)
		help_menu.addAction(about_action)
		about_action.setShortcut(QtGui.QKeySequence("Ctrl+Shift+A"))
		about_action.triggered.connect(self.openAbout)

		# use `connect` method to bind signals to desired behavior
		close_action.triggered.connect(self.close_windows)
		
		#self.setStyleSheet("""background-color:#424242;color:#f4f4f4;""");

	def setDarkMode(self, mainWindow):
		styleSheet = """
			QTreeView {
			    alternate-background-color: #605e5e;
			    background: #424242;
			}
			"""
		mainWindow.setStyleSheet("""background-color:#424242;color:#f4f4f4;""");
		mainWindow.layout.lstCommits.setStyleSheet(styleSheet)
		globalvars.darkmode = True

	def refreshConn(self):
		refreshConn()

	def openAbout(self):
		about.show()
		about.darkMode()

	def openPreference(self):
		exePath = sett.layout.readExePath()
		sett.layout.txtExePath.setText(exePath)
		sett.show()
		sett.darkMode()

	def close_windows(self):
		self.close()

	def setSQLWindowTitle(self):
		title = "SQLVC "+ globalvars.version+" - " + globalvars.server + "[" + globalvars.username + "]"
		self.setWindowTitle(title)


	def addConnection(self):
		home = expanduser("~")
		homeConfigPath = home + "/sqlvc/sqlvc-config.xml"
		readConnConfiguration(homeConfigPath, conn)
		conn.show()
		conn.darkMode()


	def center(self):
		frameGm = self.frameGeometry()
		screen = QtWidgets.QApplication.desktop().screenNumber(QtWidgets.QApplication.desktop().cursor().pos())
		centerPoint = QtWidgets.QApplication.desktop().screenGeometry(screen).center()
		frameGm.moveCenter(centerPoint)
		self.move(frameGm.topLeft())

	def openLogFolder(self):
		home = expanduser("~")
		path = home + "/sqlvc/logs"

		if platform.system() == "Windows":
			os.startfile(path)
		elif platform.system() == "Darwin":
			subprocess.Popen(["open", path])
		else:
			subprocess.Popen(["xdg-open", path])

class Layout(QtWidgets.QWidget):

	#define model for commit
	COMMIT_ID, COMMIT_USER, COMMIT_MESSAGE, COMMIT_DATE = range(4)

	def __init__(self, parent=None):
		super(Layout, self).__init__()
		# create and set layout to place widgets

		grid_layout = QtWidgets.QGridLayout(self)
		splitter = QtWidgets.QSplitter(self)

		self.fileParentTab = QtWidgets.QTabWidget()
		self.contParentTab = QtWidgets.QTabWidget()
		#self.contParentTab_layout = QtWidgets.QGridLayout(self)

		fileList = QtWidgets.QWidget()

		changesetListTab = QtWidgets.QWidget()

		self.contentTab = QtWidgets.QWidget()

		versionTab = QtWidgets.QWidget()

		self.conflictTab = QtWidgets.QWidget()

		#self.lstCommits = QtWidgets.QListWidget(self)
		self.lstCommits = QtWidgets.QTreeView(self)

		self.lstCommits.setEditTriggers(QtWidgets.QAbstractItemView.NoEditTriggers)
		self.lstCommits.setRootIsDecorated(False)
		self.lstCommits.setAlternatingRowColors(True)

		
		self.lstCommitsModel = self.createCommitModel(self)
		
		self.lstCommits.setModel(self.lstCommitsModel)
		self.lstCommits.setContextMenuPolicy(QtCore.Qt.CustomContextMenu)
		self.lstCommits.customContextMenuRequested.connect(self.openCommitMenu)
		#self.addCommit(self.lstCommitsModel, 'service@github.com','soggy', 'Your Github Donation','03/25/2017 02:05 PM')


		self.commitMessage = QtWidgets.QPlainTextEdit(self)
		self.commitMessage.setFixedHeight(70)
		self.btnCommit = QtWidgets.QPushButton("Commit")
		self.btnCommit.setMaximumWidth(100)
		self.btnCommit.clicked.connect(lambda: CommitChanges(self))


		self.objListTab = QtWidgets.QTreeWidget()
		self.objListTab.setContextMenuPolicy(QtCore.Qt.CustomContextMenu)
		self.objListTab.customContextMenuRequested.connect(self.openMenu)
		self.objListTab.setHeaderLabels(["Workspace"])
		self.objListTab.itemDoubleClicked.connect(self.generateObjectScript)

		globalvars.objListTab = self.objListTab

		#tab

		self.versionList = QtWidgets.QListWidget(self)
		self.versionList.doubleClicked.connect(self.getItemVersionInfo)


		self.conflictList = QtWidgets.QListWidget(self)

		self.lstEdited = QtWidgets.QPlainTextEdit(self)
		self.lstEdited.setReadOnly(True)
		self.lstEdited.setLineWrapMode(QtWidgets.QPlainTextEdit.NoWrap)

		self.fileParentTab.addTab(fileList, "Objects")
		self.fileParentTab.addTab(changesetListTab, "Commits")
		self.fileParentTab.setTabsClosable(True)
		self.fileParentTab.tabCloseRequested.connect(self.removeConflictTab)
		#remove close button for other tabs
		self.fileParentTab.tabBar().setTabButton(0, QtWidgets.QTabBar.RightSide,None)
		self.fileParentTab.tabBar().setTabButton(1, QtWidgets.QTabBar.RightSide,None)


		self.contParentTab.addTab(self.contentTab,"Details")
		self.contParentTab.addTab(versionTab,"Edit History")
		#self.contParentTab.addTab(self.conflictTab, "Conflicts") #hidden
		self.contParentTab.setTabsClosable(True)
		self.contParentTab.tabCloseRequested.connect(self.contParentTab.removeTab)
		#remove close button for other tabs
		self.contParentTab.tabBar().setTabButton(0, QtWidgets.QTabBar.RightSide,None)
		self.contParentTab.tabBar().setTabButton(1, QtWidgets.QTabBar.RightSide,None)

		changesetListTab.layout = QtWidgets.QGridLayout(self)
		fileList.layout = QtWidgets.QGridLayout(self)
		self.contentTab.layout = QtWidgets.QGridLayout(self)
		self.conflictTab.layout = QtWidgets.QGridLayout(self)
		versionTab.layout = QtWidgets.QGridLayout(self)

		changesetListTab.layout.addWidget(self.lstCommits, 1,0,1,1)

		fileList.layout.addWidget(self.btnCommit,0,0,1,1)
		fileList.layout.addWidget(self.commitMessage,1,0,1,1)
		fileList.layout.addWidget(self.objListTab,2,0,1,1)
		self.contentTab.layout.addWidget(self.lstEdited, 0,0, 1,2)
		self.conflictTab.layout.addWidget(self.conflictList, 0,0, 1,2)
		versionTab.layout.addWidget(self.versionList,0,0,1,1)

		changesetListTab.setLayout(changesetListTab.layout)
		fileList.setLayout(fileList.layout)
		self.contentTab.setLayout(self.contentTab.layout)
		versionTab.setLayout(versionTab.layout)
		self.conflictTab.setLayout(self.conflictTab.layout)

		# end tab

		#treeview
		#trObjList = QtWidgets.QTreeView()

		#end treeview
		splitter.addWidget(self.contParentTab)
		splitter.addWidget(self.fileParentTab)

		# grid_layout.addWidget(self.contParentTab, 1, 0, 1, 2)
		# grid_layout.addWidget(self.fileParentTab, 1, 2, 1, 2) #row, column, height, width
		grid_layout.addWidget(splitter)


		globalvars.MainWindow = self

		self.serverTypeMerge = None
		self.serverMerge = None
		self.usernameMerge = None
		self.passwordMerge = None
		self.authTypeMerge = None
		self.connected = False
		self.connString = None

	def showCommitDetails(self):
		print("hello")

	def removeConflictTab(self, index):
		self.fileParentTab.removeTab(index)
		
		tabArrIndex = (index - 2)
		del globalvars.openedCommitTab[tabArrIndex]
		del globalvars.openedCommitTabText[tabArrIndex]

	#commit table creator
	def createCommitModel(self,parent):
		model = QtGui.QStandardItemModel(0, 4, parent)
		model.setHeaderData(self.COMMIT_ID, QtCore.Qt.Horizontal, "Commit ID")
		model.setHeaderData(self.COMMIT_USER, QtCore.Qt.Horizontal, "User")
		model.setHeaderData(self.COMMIT_MESSAGE, QtCore.Qt.Horizontal, "Commit Message")
		model.setHeaderData(self.COMMIT_DATE, QtCore.Qt.Horizontal, "Date")
		return model

	def addCommit(self,model, commitID, user, message, date):
		model.insertRow(0)
		model.setData(model.index(0, self.COMMIT_ID), commitID)
		model.setData(model.index(0, self.COMMIT_USER), user)
		model.setData(model.index(0, self.COMMIT_MESSAGE), message)
		model.setData(model.index(0, self.COMMIT_DATE), date)
	#end commit table creator

	def showConflictTab(self):
		self.contParentTab.addTab(self.conflictTab, "Conflicts")
		self.contParentTab.setCurrentIndex(2)

	def getItemVersionInfo(self):
		rowId = self.versionList.selectedItems()[0].data(QtCore.Qt.UserRole)
		script = generateObjectScript(None, None, None, None, rowId)
		self.lstEdited.document().setPlainText(script);
		self.contParentTab.setCurrentIndex(0)

	def openMenu(self, position):

		indexes = self.objListTab.selectedIndexes()

		if indexes == []:
			menu = QtWidgets.QMenu()
			generate = menu.addAction(self.tr("View Object/Info"))
			generate.triggered.connect(self.generateObjectScript)

			compareLatest = menu.addAction(self.tr("Compare to latest"))
			compareLatest.triggered.connect(self.compareToLatest)

			compareVersion = menu.addAction(self.tr("Compare to other edit history"))
			compareVersion.triggered.connect(self.compareOtherVersion)

			compareCommit = menu.addAction(self.tr("Compare to other commits"))
			compareCommit.triggered.connect(self.compareOtherCommit)

			removeObj = menu.addAction(self.tr("Delete to Workspace"))
			removeObj.triggered.connect(self.removeObj)

			inexclude = menu.addAction(self.tr("Include/Exclude"))
			inexclude.triggered.connect(self.inexclude)

			menu.exec_(self.objListTab.viewport().mapToGlobal(position))

	def openCommitMenu(self, position):
		indexes = self.lstCommits.selectedIndexes()
		if len(indexes) > 0:
			menu = QtWidgets.QMenu()
			generate = menu.addAction(self.tr("View Commit Info"))
			generate.triggered.connect(lambda:self.generateCommitObjectList(self.lstCommitsModel.data(indexes[0]), self.lstCommitsModel.data(indexes[2]), 'viewcommit'))

			# mergeCommit = menu.addAction(self.tr("Merge to other server"))
			# mergeCommit.triggered.connect(lambda:self.generateMergeCommitObjectList(self.lstCommitsModel.data(indexes[0]), self.lstCommitsModel.data(indexes[2])))

			menu.exec_(self.lstCommits.viewport().mapToGlobal(position))


	def generateMergeCommitObjectList(self):
		# globalvars.connectionMode = 'mergeserver'
		# #conn.layout.setButtonFunction(self)

		if self.connected:
			self.txtCommitID.show()
			self.btnCommitMerge.hide()

			self.btnOpenServer.setText("Apply to...")
			self.btnOpenServer.clicked.connect(self.generateMergeCommitObjectList)

			conn.layout.btnOpen.disconnect()
			conn.layout.btnOpen.clicked.connect(lambda: OpenConnection(conn.layout))

			self.commitList.customContextMenuRequested.disconnect()
			self.commitList.customContextMenuRequested.connect(self.openCommitDetailsMenu)
			self.txtCommitMessage.setReadOnly(True)

			self.connected = False
		else:

			conn.layout.btnOpen.disconnect()
			conn.layout.btnOpen.clicked.connect(self.OpenConnectionMerge)
			conn.show()

			self.commitList.customContextMenuRequested.disconnect()
			self.commitList.customContextMenuRequested.connect(self.openMergeCommitDetailsMenu)

		# #gnerate list
		# self.generateCommitObjectList(commitid, commitMessage, 'mergecommit')



	def OpenConnectionMerge(self):

		try:
			serverType = conn.layout.cmbDbase.currentText()
			server = conn.layout.cmbServers.currentText()
			username = conn.layout.txtUserName.text()
			password = conn.layout.txtPassword.text()
			authType = conn.layout.cmbAuthType.currentText()

			stat = testConn(serverType, server, authType, username, password)
			if stat:
				configPath = os.path.expanduser("~") + "/sqlvc/sqlvc-config.xml"
				saveConfigurations(configPath, conn.layout)

				globalvars.engine = serverType
				self.serverTypeMerge = conn.layout.cmbDbase.currentText()
				self.serverMerge = conn.layout.cmbServers.currentText()
				self.usernameMerge = conn.layout.txtUserName.text()
				self.passwordMerge = conn.layout.txtPassword.text()
				self.authTypeMerge = conn.layout.cmbAuthType.currentText()
				self.connected = True

				if self.authTypeMerge == "Windows Authentication":
					self.connString = "DRIVER={" + globalvars.SQLSERVER + "};SERVER=" + self.serverMerge + ";DATABASE=SQLVC;Trusted_Connection=yes;"
				else:
					self.connString = "DRIVER={" + globalvars.SQLSERVER + "};SERVER=" + self.serverMerge + ";DATABASE=SQLVC;UID=" + self.usernameMerge + ";PWD=" + self.passwordMerge

				#set button text
				self.btnOpenServer.setText("Disconnect")
				#setup ui
				self.txtCommitID.hide()
				self.btnCommitMerge.show()
				self.txtCommitMessage.setReadOnly(False)

				print("Successfully connected to target database")


				conn.layout.btnCancel.click()

			else:
				error_message = "Could not connect to database server!"
				QtWidgets.QMessageBox.about(conn.layout, "Error", error_message)

			#return to default in case user wants to connect to other server
			globalvars.connectionMode == 'connectserver' 
			conn.layout.btnOpen.disconnect()
			conn.layout.btnOpen.clicked.connect(lambda: OpenConnection(conn.layout))

		except Exception as e:
			saveLog(traceback.format_exc())
			print("Connection error occured for merge")

	def openMergeCommitDetailsMenu(self, position):
		indexes = self.commitList.selectedIndexes()
		if len(indexes) == 0:
			menu = QtWidgets.QMenu()
			generate = menu.addAction(self.tr("Merge to " + self.serverMerge))
			generate.triggered.connect(self.mergeToTarget)
			menu.exec_(self.commitList.viewport().mapToGlobal(position))

	def mergeToTarget(self):
		if self.commitList.selectedIndexes() == []:
			item = self.commitList.currentItem()
			itemText = item.text(0)

			dbObjType = item.parent()
			dbObjTypeText = dbObjType.text(0)

			database = dbObjType.parent()
			databaseText = database.text(0)
			
			downloadToCompare(globalvars.username, databaseText, dbObjTypeText, itemText, databaseText, dbObjTypeText, itemText, 'compareToServer', self.txtCommitID.text(), '', '', self.serverMerge, '', self.usernameMerge, '', self.passwordMerge, '', self.authTypeMerge)


	def openCommitDetailsMenu(self, position):
		indexes = self.commitList.selectedIndexes()
		if len(indexes) == 0:
			menu = QtWidgets.QMenu()
			generate = menu.addAction(self.tr("Compare to other commit"))
			generate.triggered.connect(self.compareToOtherCommit)
			#generate.triggered.connect(lambda:self.generateCommitObjectList(self.lstCommitsModel.data(indexes[0]), self.lstCommitsModel.data(indexes[2])))

			menu.exec_(self.commitList.viewport().mapToGlobal(position))

	def compareToOtherCommit(self):
		print("Comparing to other commit")
		globalvars.compareObj.layout.compareToOtherCommits(self.commitList)
		globalvars.commit1 = self.txtCommitID.text()

		compare.show()
		compare.darkMode()

		globalvars.compareMode = "comparecommit2"


	def generateCommitObjectList(self, commitid, commitMessage, mode):
		if commitid not in globalvars.openedCommitTabText:
			commitInfo = QtWidgets.QWidget()

			commitTitle = "Commit [" + commitid + "]"

			self.commitid = commitid

			self.fileParentTab.addTab(commitInfo, commitTitle)
			commitInfo.layout = QtWidgets.QGridLayout(self)
			commitInfo.setLayout(commitInfo.layout)

			self.txtCommitID = QtWidgets.QLineEdit(self)
			commitInfo.layout.addWidget(self.txtCommitID,0,1,1,1)
			self.txtCommitID.setReadOnly(True)
			self.txtCommitID.setText(commitid)

			self.txtCommitMessage = QtWidgets.QPlainTextEdit(self)
			commitInfo.layout.addWidget(self.txtCommitMessage,1,0,1,3)
			self.txtCommitMessage.setFixedHeight(70)
			self.txtCommitMessage.setReadOnly(True)
			self.txtCommitMessage.document().setPlainText(commitMessage)

			self.btnOpenServer = QtWidgets.QPushButton("Apply to...")
			commitInfo.layout.addWidget(self.btnOpenServer,0,0,1,1)
			self.btnOpenServer.clicked.connect(self.generateMergeCommitObjectList)
			self.btnOpenServer.setMaximumWidth(110)

			self.btnCommitMerge = QtWidgets.QPushButton("Commit")
			commitInfo.layout.addWidget(self.btnCommitMerge,0,1,1,1)
			self.btnCommitMerge.clicked.connect(lambda: CommitChanges(self, 'mergeToTarget'))
			self.btnCommitMerge.setMaximumWidth(100)
			self.btnCommitMerge.hide()
			#self.btnOpenServer.clicked.connect(lambda: CommitChanges(self))

			self.commitList = QtWidgets.QTreeWidget()
			commitInfo.layout.addWidget(self.commitList,2,0,3,3)
			self.commitList.setHeaderLabels([commitid])
			self.commitList.itemDoubleClicked.connect(self.generateCommitScript)
			self.commitList.setContextMenuPolicy(QtCore.Qt.CustomContextMenu)
			self.commitList.customContextMenuRequested.connect(self.openCommitDetailsMenu)

			self.commitList.clear()

			dataBaseCommits = getCommitDetails(commitid)
			
			trViewObjects = treeModel()
			trViewObjects.generateView(self.commitList, dataBaseCommits)

			globalvars.openedCommitTabText.append(commitid)
			globalvars.openedCommitTab.append(commitInfo)

		objIndex = globalvars.openedCommitTabText.index(commitid)
		self.fileParentTab.setCurrentIndex((2 + objIndex))

	def generateCommitScript(self):
		print("Viewing script info")
		if self.commitList.selectedIndexes() == []:
			item = self.commitList.currentItem()
			itemText = item.text(0)

			dbObjType = item.parent()
			dbObjTypeText = dbObjType.text(0)

			database = dbObjType.parent()
			databaseText = database.text(0)

			objScript = generateCommitScript(None, databaseText, dbObjTypeText, itemText, self.commitid)

			self.versionList.clear() #clear items first
			self.lstEdited.document().setPlainText(objScript);

	def removeObj(self):
		print("Remove item")
		if self.objListTab.selectedIndexes() == []:
			item = self.objListTab.currentItem()
			# itemText = item.text(0)

			# dbObjType = item.parent()
			# dbObjTypeText = dbObjType.text(0)

			# database = dbObjType.parent()
			# databaseText = database.text(0)
			rowId = item.data(QtCore.Qt.UserRole,0)

			#removeItemToWorkspace(globalvars.username, databaseText, dbObjTypeText, itemText)
			removeItemToWorkspace(rowId)


	def inexclude(self):
		print("Include/Exclude item")
		if self.objListTab.selectedIndexes() == []:
			item = self.objListTab.currentItem()
			if item.checkState(0) == QtCore.Qt.Unchecked:
				item.setCheckState(0,QtCore.Qt.Checked)
			else:
				item.setCheckState(0,QtCore.Qt.Unchecked)

	def compareOtherVersion(self):
		globalvars.compareObj.layout.compareToOtherVersions()
		globalvars.compareObj.setWindowFlags(globalvars.compareObj.windowFlags() | QtCore.Qt.WindowStaysOnTopHint)

		compare.show()
		compare.darkMode()

		globalvars.compareMode = "compareversion"

	def compareOtherCommit(self):
		globalvars.compareObj.layout.compareToOtherCommits(self.objListTab)
		compare.show()
		compare.darkMode()
		globalvars.compareMode = "comparecommit"

	def compareToLatest(self):
		print("Comparing to latest version")
		if self.objListTab.selectedIndexes() == []:
			item = self.objListTab.currentItem()
			itemText = item.text(0)

			dbObjType = item.parent()
			dbObjTypeText = dbObjType.text(0)

			database = dbObjType.parent()
			databaseText = database.text(0)

			downloadToCompare(globalvars.username, databaseText, dbObjTypeText, itemText, databaseText, dbObjTypeText, itemText, 'compareLatest')

	def generateObjectScript(self):
		print("Viewing script info")
		if self.objListTab.selectedIndexes() == []:
			item = self.objListTab.currentItem()
			itemText = item.text(0)

			dbObjType = item.parent()
			dbObjTypeText = dbObjType.text(0)

			database = dbObjType.parent()
			databaseText = database.text(0)

			objScript = generateObjectScript(globalvars.username, databaseText, dbObjTypeText, itemText)
			versionList = generateVersionList(databaseText, dbObjTypeText, itemText)

			latest = " ("+globalvars.username+"'s latest version)"

			self.versionList.clear() #clear items first
			for version in versionList: #iterate
				#latest by user flag
				flag = ""
				if version[1] == globalvars.username:
					flag = latest
					latest = ""

				item = QtWidgets.QListWidgetItem(version[2] + '.' + version[3] + '.' + version[4] + ' modified last ' + str(version[5]) + ' by ' + version[1] + flag)
				item.setData(QtCore.Qt.UserRole, version[6])
				#item.itemDoubleClicked.connect(lambda:generateObjectScript(None, None, None, None, version[6]))
				self.versionList.addItem(item)

			self.lstEdited.document().setPlainText(objScript);


if __name__ == '__main__':
	app = QtWidgets.QApplication(sys.argv)
	# creating main window
	mw = MainWindow()
	mw.show()

	conn = ConnectionWindow()

	sett = SettingsWindow()

	compare = CompareOther()

	about = AboutWindow()
	
	sys.exit(app.exec_())