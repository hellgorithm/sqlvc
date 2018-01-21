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
import webbrowser

try:
    import urllib.request as urllib2
    update = "urllib"
except ImportError:
    import urllib2
    update = "urllib2"

import traceback

class MainWindow(QtWidgets.QMainWindow):
	def __init__(self, parent=None):
		super(MainWindow,self).__init__()

		#initialize window
		self.layout = Layout(parent=self)
		self.setWindowTitle("SQLVC " + globalvars.version)
		self.setWindowIcon(QtGui.QIcon('icons/sqlvc-icon.png'))
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

		# dark_action = QtWidgets.QAction('&Dark Mode', self, checkable=True)
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

		self.restoreState()
		
		#self.setStyleSheet("""background-color:#424242;color:#f4f4f4;""");
	
	def checkUpdates(self):
		try:
			data = urllib2.urlopen(globalvars.version_url)
			dl_msg = ""
			
			if update == "urllib2":
				for line in data:
					if str(globalvars.version) != str(line.replace("\n", "")):
						dl_msg = "SQLVC " + str(line.replace("\n", "")) + " is now available. Download now?"
			else:
				version = str(data.read().decode('UTF-8')).replace("\n", "")
				
				if str(globalvars.version) != str(version):
					dl_msg = "SQLVC " + version + " is now available. Download now?"

			if len(dl_msg) > 0:
				reply = QtWidgets.QMessageBox.question(globalvars.MainWindow, "Updates available", dl_msg,  QtWidgets.QMessageBox.Ok,  QtWidgets.QMessageBox.Cancel)
				if reply == QtWidgets.QMessageBox.Ok:
					webpage = globalvars.dl_url
					webbrowser.open_new_tab(webpage)

		except Exception as e:
			saveLog(traceback.format_exc())
			print("Connection error occured for merge")

	def setDarkMode(self, mainWindow):
		styleSheet = """
			QTreeView {
			    alternate-background-color: #605e5e;
			    background: #424242;
			}

			QTabBar::tab {
				background: #38393b;
			}
			"""
		mainWindow.setStyleSheet("""background-color:#424242;color:#f4f4f4;""");
		mainWindow.layout.lstCommits.setStyleSheet(styleSheet)
		mainWindow.layout.fileParentTab.setStyleSheet(styleSheet)
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

	def closeEvent(self, event):
		self.settings = QtCore.QSettings("SQLVC", "sqlvc_app")
		self.settings.setValue("geometry", self.saveGeometry())
		self.settings.setValue("windowState", self.saveState())
		self.settings.setValue("splitterSettings", self.layout.splitter.saveState())

	def restoreState(self):
		self.settings = QtCore.QSettings("SQLVC", "sqlvc_app")

		if not self.settings.value("geometry") == None:
			self.restoreGeometry(self.settings.value("geometry"))

		if not self.settings.value("windowState") == None:
			self.restoreState(self.settings.value("windowState"))

		if self.settings.value("splitterSettings"):
			self.layout.splitter.restoreState(self.settings.value("splitterSettings"))


	def setSQLWindowTitle(self):
		title = "SQLVC "+ globalvars.version+" - " + globalvars.server + "[" + globalvars.username + "]"
		self.setWindowTitle(title)


	def addConnection(self):
		conn.layout.cmbServers.clear()
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
		self.splitter = QtWidgets.QSplitter(self)

		self.fileParentTab = QtWidgets.QTabWidget()
		self.contParentTab = QtWidgets.QTabWidget()
		self.fileParentTab.currentChanged.connect(self.initData)
		#self.contParentTab_layout = QtWidgets.QGridLayout(self)

		fileList = QtWidgets.QWidget()

		changesetListTab = QtWidgets.QWidget()

		shelveListTab = QtWidgets.QWidget()

		#self.contentTab = QtWidgets.QWidget()

		versionTab = QtWidgets.QWidget()

		self.conflictTab = QtWidgets.QWidget()

		#============================================================================
		self.lstCommits = QtWidgets.QTreeView(self)

		self.lstCommits.setEditTriggers(QtWidgets.QAbstractItemView.NoEditTriggers)
		self.lstCommits.setRootIsDecorated(False)
		self.lstCommits.setAlternatingRowColors(True)

		
		self.lstCommitsModel = self.createCommitModel(self)
		self.lstCommits.setModel(self.lstCommitsModel)
		self.lstCommits.setContextMenuPolicy(QtCore.Qt.CustomContextMenu)
		self.lstCommits.customContextMenuRequested.connect(self.openCommitMenu)

		#=============================================================================

		self.lstShelve = QtWidgets.QTreeView(self)

		self.lstShelve.setEditTriggers(QtWidgets.QAbstractItemView.NoEditTriggers)
		self.lstShelve.setRootIsDecorated(False)
		self.lstShelve.setAlternatingRowColors(True)

		self.lstShelveModel = self.createShelveModel(self)
		self.lstShelve.setModel(self.lstShelveModel)
		self.lstShelve.setContextMenuPolicy(QtCore.Qt.CustomContextMenu)
		self.lstShelve.customContextMenuRequested.connect(self.openShelveMenu)
		#self.addCommit(self.lstCommitsModel, 'service@github.com','soggy', 'Your Github Donation','03/25/2017 02:05 PM')


		self.commitMessage = QtWidgets.QPlainTextEdit(self)
		self.commitMessage.setFixedHeight(70)
		self.commitMessage.setPlaceholderText("Enter commit/shelve message") 

		self.btnCommit = QtWidgets.QPushButton("Commit")
		self.btnCommit.setMaximumWidth(100)
		self.btnCommit.clicked.connect(lambda: CommitChanges(self))

		self.btnShelve = QtWidgets.QPushButton("Shelve")
		self.btnShelve.clicked.connect(lambda: ShelveChanges(self))
		self.btnShelve.setMaximumWidth(100)


		self.txtSearch = QtWidgets.QLineEdit(self)
		self.txtSearch.setPlaceholderText("Filter Objects") 
		self.txtSearch.textChanged.connect(self.filterObjects)

		self.objListTab = QtWidgets.QTreeWidget()
		self.objListTab.setContextMenuPolicy(QtCore.Qt.CustomContextMenu)
		self.objListTab.customContextMenuRequested.connect(self.openMenu)
		self.objListTab.setHeaderLabels(["Workspace"])
		self.objListTab.itemDoubleClicked.connect(self.generateObjectScript)

		globalvars.objListTab = self.objListTab

		#tab

		self.versionList = QtWidgets.QListWidget(self)
		self.versionList.setAlternatingRowColors(True);
		self.versionList.doubleClicked.connect(self.getItemVersionInfo)


		self.conflictList = QtWidgets.QListWidget(self)

		#self.lstEdited = QtWidgets.QPlainTextEdit(self)
		#self.lstEdited.setReadOnly(True)
		#self.lstEdited.setLineWrapMode(QtWidgets.QPlainTextEdit.NoWrap)

		self.fileParentTab.addTab(fileList, "Objects")
		self.fileParentTab.addTab(versionTab, "Edit History")
		self.fileParentTab.addTab(changesetListTab, "Commits")
		self.fileParentTab.addTab(shelveListTab, "Shelf") #feature hold

		self.fileParentTab.setTabsClosable(True)
		self.fileParentTab.tabCloseRequested.connect(self.removeCommitTab)
		#remove close button for other tabs
		self.fileParentTab.tabBar().setTabButton(0, QtWidgets.QTabBar.RightSide,None)
		self.fileParentTab.tabBar().setTabButton(1, QtWidgets.QTabBar.RightSide,None)
		self.fileParentTab.tabBar().setTabButton(2, QtWidgets.QTabBar.RightSide,None)
		self.fileParentTab.tabBar().setTabButton(3, QtWidgets.QTabBar.RightSide,None)


		#self.contParentTab.addTab(self.contentTab,"Details")
		#self.contParentTab.addTab(versionTab,"Edit History")
		#self.contParentTab.addTab(self.conflictTab, "Conflicts") #hidden
		self.contParentTab.setTabsClosable(True)
		self.contParentTab.tabCloseRequested.connect(self.contParentTab.removeTab)
		#remove close button for other tabs
		#self.contParentTab.tabBar().setTabButton(0, QtWidgets.QTabBar.RightSide,None)
		#self.contParentTab.tabBar().setTabButton(1, QtWidgets.QTabBar.RightSide,None)

		#====================================================================================
		changesetListTab.layout = QtWidgets.QGridLayout(self)
		fileList.layout = QtWidgets.QGridLayout(self)
		shelveListTab.layout = QtWidgets.QGridLayout(self)
		#self.contentTab.layout = QtWidgets.QGridLayout(self)
		self.conflictTab.layout = QtWidgets.QGridLayout(self)
		versionTab.layout = QtWidgets.QGridLayout(self)
		#====================================================================================

		changesetListTab.layout.addWidget(self.lstCommits, 1,0,1,1)
		shelveListTab.layout.addWidget(self.lstShelve, 1,0,1,1)

		fileList.layout.addWidget(self.btnCommit,0,0,1,1)
		fileList.layout.addWidget(self.btnShelve,0,1,1,1)
		fileList.layout.addWidget(self.commitMessage,1,0,1,4)
		fileList.layout.addWidget(self.txtSearch,2,0,1,4)
		fileList.layout.addWidget(self.objListTab,3,0,1,4)

		#self.contentTab.layout.addWidget(self.lstEdited, 0,0, 1,2)
		self.conflictTab.layout.addWidget(self.conflictList, 0,0, 1,2)
		versionTab.layout.addWidget(self.versionList,0,0,1,1)

		changesetListTab.setLayout(changesetListTab.layout)
		shelveListTab.setLayout(shelveListTab.layout)

		fileList.setLayout(fileList.layout)
		#self.contentTab.setLayout(self.contentTab.layout)
		versionTab.setLayout(versionTab.layout)
		self.conflictTab.setLayout(self.conflictTab.layout)

		self.viewHistoryDetail()
		# end tab

		#treeview
		#trObjList = QtWidgets.QTreeView()

		#end treeview
		self.splitter.addWidget(self.contParentTab)
		self.splitter.addWidget(self.fileParentTab)

		# grid_layout.addWidget(self.contParentTab, 1, 0, 1, 2)
		# grid_layout.addWidget(self.fileParentTab, 1, 2, 1, 2) #row, column, height, width
		grid_layout.addWidget(self.splitter)


		globalvars.MainWindow = self

		self.serverTypeMerge = None
		self.serverMerge = None
		self.usernameMerge = None
		self.passwordMerge = None
		self.authTypeMerge = None
		self.connected = False
		self.connString = None

	# def keyPressEvent(self, widget, e):
	# 	QtWidgets.QLineEdit.keyPressEvent(widget, e)

	def viewHistoryDetail(self):
		self.lstEdited = QtWidgets.QPlainTextEdit(self)
		self.lstEdited.setReadOnly(True)
		self.lstEdited.setLineWrapMode(QtWidgets.QPlainTextEdit.NoWrap)

		self.contentTab = QtWidgets.QWidget()
		self.contentTab.layout = QtWidgets.QGridLayout(self)

		self.contentTab.layout.addWidget(self.lstEdited, 0,0, 1,2)
		self.contentTab.setLayout(self.contentTab.layout)

		self.contParentTab.addTab(self.contentTab,"Details")
		self.contParentTab.tabBar().setTabButton(0, QtWidgets.QTabBar.RightSide,None)

	def filterObjects(self):
		value = self.txtSearch.text()

		if len(globalvars.databaseEdits) > 0:
			globalvars.objListTab.clear()
			trViewObjects = treeModel()
			trViewObjects.generateView(globalvars.objListTab, globalvars.databaseEdits, value)


	# def filterObjects(self):
	# 	print("hello")

	def removeCommitTab(self, index):
		self.fileParentTab.removeTab(index)
		
		tabArrIndex = (index - 4)
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

	def createShelveModel(self,parent):
		model = QtGui.QStandardItemModel(0, 4, parent)
		model.setHeaderData(self.COMMIT_ID, QtCore.Qt.Horizontal, "Shelve ID")
		model.setHeaderData(self.COMMIT_USER, QtCore.Qt.Horizontal, "User")
		model.setHeaderData(self.COMMIT_MESSAGE, QtCore.Qt.Horizontal, "Shelve Message")
		model.setHeaderData(self.COMMIT_DATE, QtCore.Qt.Horizontal, "Date")
		return model

	def addShelve(self,model, shelveID, user, message, date):
		model.insertRow(0)
		model.setData(model.index(0, self.COMMIT_ID), shelveID)
		model.setData(model.index(0, self.COMMIT_USER), user)
		model.setData(model.index(0, self.COMMIT_MESSAGE), message)
		model.setData(model.index(0, self.COMMIT_DATE), date)
	#end commit table creator

	def showConflictTab(self):
		self.contParentTab.addTab(self.conflictTab, "Conflicts")
		self.contParentTab.setCurrentIndex(1)

	def getItemVersionInfo(self):
		rowId = self.versionList.selectedItems()[0].data(QtCore.Qt.UserRole)
		script = generateObjectScript(None, None, None, None, rowId)
		self.lstEdited.document().setPlainText(script);
		self.contParentTab.setCurrentIndex(0)

	def openMenu(self, position):

		indexes = self.objListTab.selectedIndexes()
		
		item = self.objListTab.currentItem()

		if item != None:
			
			menu = QtWidgets.QMenu()

			if indexes == []:

				itemText = item.text(0)

				dbObjType = item.parent()
				dbObjTypeText = dbObjType.text(0)

				database = dbObjType.parent()
				databaseText = database.text(0)


				if 'TABLE' in dbObjTypeText or 'COLUMN' in dbObjTypeText:
					generate = menu.addAction(self.tr("View Schema"))
					generate.triggered.connect(self.generateObjectScript)

					generate = menu.addAction(self.tr("Compile Edit History(commit script)"))
					generate.triggered.connect(lambda: self.viewEditHistoryCompile(databaseText, dbObjTypeText, itemText))
				else:
					generate = menu.addAction(self.tr("View Object/Info"))
					generate.triggered.connect(self.generateObjectScript)

					#compareLatest = menu.addAction(self.tr("Compare to latest"))
					compareLatest = menu.addAction(self.tr("Compare to latest edit"))
					compareLatest.triggered.connect(self.compareToLatest)

					compareVersion = menu.addAction(self.tr("Compare to other edit history"))
					compareVersion.triggered.connect(self.compareOtherVersion)

					compareCommit = menu.addAction(self.tr("Compare to other commits"))
					compareCommit.triggered.connect(self.compareOtherCommit)

				inexclude = menu.addAction(self.tr("Include/Exclude"))
				inexclude.triggered.connect(self.inexclude)

			else:


				includeAll = menu.addAction(self.tr("Include All"))
				includeAll.triggered.connect(lambda:self.getAllChildren('include'))

				excludeAll = menu.addAction(self.tr("Exclude All"))
				excludeAll.triggered.connect(lambda:self.getAllChildren('exclude'))


			removeObj = menu.addAction(self.tr("Delete to Workspace"))
			removeObj.triggered.connect(self.removeObj)

				#menu.exec_(self.objListTab.viewport().mapToGlobal(position))

			
			# undo = menu.addAction(self.tr("Undo"))
			# undo.triggered.connect(lambda:self.rollbackEdits('count'))
			menu.exec_(self.objListTab.viewport().mapToGlobal(position))

	def getAllChildren(self, mode = ''):
		item = self.objListTab.currentItem()
		# print(item.childCount())

		# print(item.child(0))

		# print(item.parentCount())

		selected_item = []

		if item.childCount() == 0:
			if mode == 'select':
				rowId = item.data(QtCore.Qt.UserRole,0)
				selected_item.append(str(rowId))
			else:
				self.includeExclude(item, mode)
		else:
			for i in range(item.childCount()):

				child1 = item.child(i)

				if child1.childCount() == 0:
					if mode == 'select':
						rowId = child1.data(QtCore.Qt.UserRole,0)
						selected_item.append(str(rowId))
					else:
						self.includeExclude(child1, mode)

				for j in range(child1.childCount()):

					child2 = child1.child(j)

					if child2.childCount() == 0:
						if mode == 'select':
							rowId = child2.data(QtCore.Qt.UserRole,0)
							selected_item.append(str(rowId))
						else:
							self.includeExclude(child2, mode)

					for k in range(child2.childCount()):

						child3 = child2.child(k)

						if child3.childCount() == 0:
							if mode == 'select':
								rowId = child3.data(QtCore.Qt.UserRole,0)
								selected_item.append(str(rowId))
							else:
								self.includeExclude(child3, mode)

						for l in range(child3.childCount()):
							
							child4 = child3.child(l)

							if child4.childCount() == 0:
								if mode == 'select':
									rowId = child4.data(QtCore.Qt.UserRole,0)
									selected_item.append(str(rowId))
								else:
									self.includeExclude(child4, mode)

		return selected_item

		# item = treeView.invisibleRootItem()
		# selected_items = select_item(item)
	def includeExclude(self, item, mode):
		if mode == 'include':
			item.setCheckState(0,QtCore.Qt.Checked)
		else:
			item.setCheckState(0,QtCore.Qt.Unchecked)

	def openCommitMenu(self, position):
		indexes = self.lstCommits.selectedIndexes()
		if len(indexes) > 0:
			menu = QtWidgets.QMenu()
			generate = menu.addAction(self.tr("View Commit Info"))
			generate.triggered.connect(lambda:self.generateDatabaseObjectList(self.lstCommitsModel.data(indexes[0]), self.lstCommitsModel.data(indexes[2]), 'viewcommit'))

			# mergeCommit = menu.addAction(self.tr("Merge to other server"))
			# mergeCommit.triggered.connect(lambda:self.generateMergeCommitObjectList(self.lstCommitsModel.data(indexes[0]), self.lstCommitsModel.data(indexes[2])))

			menu.exec_(self.lstCommits.viewport().mapToGlobal(position))

	def openShelveMenu(self, position):
		indexes = self.lstShelve.selectedIndexes()
		if len(indexes) > 0:
			menu = QtWidgets.QMenu()
			generate = menu.addAction(self.tr("View shelf details"))
			#generate.triggered.connect(lambda:self.applyShelveToworkspace(self.lstShelveModel.data(indexes[0])))
			generate.triggered.connect(lambda:self.generateDatabaseObjectList(self.lstShelveModel.data(indexes[0]), self.lstShelveModel.data(indexes[2]), 'viewshelve'))
			menu.exec_(self.lstShelve.viewport().mapToGlobal(position))

	def viewEditHistoryCompile(self, databaseText, dbObjTypeText, itemText):
		print("Show edit history compile window")
		versionList = generateVersionList(databaseText, dbObjTypeText, itemText)
		compHist.layout.setEditData(versionList)
		compHist.show()

	def generateMergeCommitObjectList(self):
		# globalvars.connectionMode = 'mergeserver'
		# #conn.layout.setButtonFunction(self)

		if self.connected:
			self.txtCommitID.show()
			self.btnPatch.show()

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

			# self.commitList.customContextMenuRequested.disconnect()
			# self.commitList.customContextMenuRequested.connect(self.openMergeCommitDetailsMenu)

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
				saveConfigurations(configPath, conn.layout, 'nosave')

				globalvars.engine = serverType
				self.serverTypeMerge = conn.layout.cmbDbase.currentText()
				self.serverMerge = conn.layout.cmbServers.currentText()
				self.usernameMerge = conn.layout.txtUserName.text()
				self.passwordMerge = conn.layout.txtPassword.text()
				self.authTypeMerge = conn.layout.cmbAuthType.currentText()
				self.connected = True
				self.commitList.customContextMenuRequested.disconnect()
				self.commitList.customContextMenuRequested.connect(self.openMergeCommitDetailsMenu)

				if self.authTypeMerge == "Windows Authentication":
					self.connString = "DRIVER={" + globalvars.SQLSERVER + "};SERVER=" + self.serverMerge + ";DATABASE=SQLVC;Trusted_Connection=yes;"
				else:
					self.connString = "DRIVER={" + globalvars.SQLSERVER + "};SERVER=" + self.serverMerge + ";DATABASE=SQLVC;UID=" + self.usernameMerge + ";PWD=" + self.passwordMerge

				#set button text
				self.btnOpenServer.setText("Disconnect")
				#setup ui
				self.txtCommitID.hide()
				self.btnPatch.hide()

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
			server = self.serverMerge
			generate = menu.addAction(self.tr("Merge to " + server))
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
		item = self.commitList.currentItem()
		if len(indexes) == 0:
			menu = QtWidgets.QMenu()

			if self.mode == 'viewcommit':
				generate = menu.addAction(self.tr("Compare to other commit"))
				generate.triggered.connect(self.compareToOtherCommit)

			if self.mode == "viewshelve":
				if 'TABLE' in item.parent().text(0) or 'COLUMN' in item.parent().text(0):
					generate = menu.addAction(self.tr("Add to workspace"))
					generate.triggered.connect(self.applyShelveToworkspace)
				else:
					generate = menu.addAction(self.tr("Compare latest version"))
					generate.triggered.connect(self.compareShelfToLates)

			#latestVersion = menu.addAction(self.tr("Compare to latest version"))
			#latestVersion = menu.addAction(self.tr("Rollback"))
			#generate.triggered.connect(lambda:self.generateCommitObjectList(self.lstCommitsModel.data(indexes[0]), self.lstCommitsModel.data(indexes[2])))

			menu.exec_(self.commitList.viewport().mapToGlobal(position))

	def compareToOtherCommit(self):
		print("Comparing to other commit")
		globalvars.compareObj.layout.compareToOtherCommits(self.commitList)
		globalvars.commit1 = self.txtCommitID.text()

		compare.show()
		compare.darkMode()

		globalvars.compareMode = "comparecommit2"

	def applyShelveToworkspace(self, shelveid):
		try:
			if self.commitList.selectedIndexes() == []:
				item = self.commitList.currentItem()
				itemText = item.text(0)

				dbObjType = item.parent()
				dbObjTypeText = dbObjType.text(0)

				database = dbObjType.parent()
				databaseText = database.text(0)

				shelveid = self.txtCommitID.text()

				query = get_scripts_apply_shelve(shelveid, databaseText, dbObjTypeText, itemText)
				print(query)
				conn = pyodbc.connect(globalvars.connString, autocommit=True)
				cursor = conn.cursor()
				cursor.execute(query)
				getUserObject()

				error_message = "Shelved file has been restored."
				QtWidgets.QMessageBox.question(globalvars.MainWindow, "Shelve Scripts", error_message,  QtWidgets.QMessageBox.Ok)
		except Exception as e:
			saveLog(traceback.format_exc())
			print("Error creating applying shelve! Please see log file")
			error_message = "Error creating patch file! Please see log file"
			QtWidgets.QMessageBox.question(globalvars.MainWindow, "Shelve Scripts", error_message,  QtWidgets.QMessageBox.Ok)



	def generateDatabaseObjectList(self, commitid, commitMessage, mode):
		if commitid not in globalvars.openedCommitTabText:
			self.commitInfo = QtWidgets.QWidget()
			self.mode = mode
			if self.mode == "viewcommit":
				commitTitle = "Commit [" + commitid + "]"

			if self.mode == "viewshelve":
				commitTitle = "Shelved [" + commitid + "]"

			self.dataid = commitid

			self.fileParentTab.addTab(self.commitInfo, commitTitle)
			self.commitInfo.layout = QtWidgets.QGridLayout(self)
			self.commitInfo.setLayout(self.commitInfo.layout)

			# self.txtCommitID = QtWidgets.QLineEdit(self) #0
			# self.commitInfo.layout.addWidget(self.txtCommitID,0,2,1,1)
			# self.txtCommitID.setReadOnly(True)
			# self.txtCommitID.setText(self.dataid)

			self.txtCommitMessage = QtWidgets.QPlainTextEdit(self) #0
			self.commitInfo.layout.addWidget(self.txtCommitMessage,1,0,1,3)
			self.txtCommitMessage.setFixedHeight(70)
			self.txtCommitMessage.setReadOnly(True)
			self.txtCommitMessage.document().setPlainText(commitMessage)

			if mode == "viewcommit":
				self.txtCommitID = QtWidgets.QLineEdit(self) #0
				self.commitInfo.layout.addWidget(self.txtCommitID,0,2,1,1)
				self.txtCommitID.setReadOnly(True)
				self.txtCommitID.setText(self.dataid)

				self.btnOpenServer = QtWidgets.QPushButton("Apply to...") #0
				self.commitInfo.layout.addWidget(self.btnOpenServer,0,0,1,1)
				self.btnOpenServer.clicked.connect(self.generateMergeCommitObjectList)
				self.btnOpenServer.setMaximumWidth(110)

				self.btnCommitMerge = QtWidgets.QPushButton("Commit") #1
				self.commitInfo.layout.addWidget(self.btnCommitMerge,0,1,1,1)
				self.btnCommitMerge.clicked.connect(lambda: commitToOtherServer(self))
				self.btnCommitMerge.setMaximumWidth(100)
				self.btnCommitMerge.hide()

				self.btnPatch = QtWidgets.QPushButton("Create Patch") #2
				self.commitInfo.layout.addWidget(self.btnPatch,0,1,1,1)
				self.btnPatch.clicked.connect(self.createPatch)
				self.btnPatch.setMaximumWidth(100)
				#self.btnOpenServer.clicked.connect(lambda: CommitChanges(self))

				self.dataBaseCommits = getCommitDetails(commitid)

			if mode == "viewshelve":

				self.txtCommitID = QtWidgets.QLineEdit(self) #0
				self.commitInfo.layout.addWidget(self.txtCommitID,0,0,1,1)
				self.txtCommitID.setReadOnly(True)
				self.txtCommitID.setText(self.dataid)

				self.dataBaseCommits = getSheveDetails(commitid, globalvars.username)

			self.txtCommitFilter = QtWidgets.QLineEdit(self) #1
			self.txtCommitFilter.textChanged.connect(lambda:self.filterCommitObjects(mode))
			self.txtCommitFilter.setPlaceholderText("Filter commit objects") 
			self.commitInfo.layout.addWidget(self.txtCommitFilter,2,0,1,3)

			self.commitList = QtWidgets.QTreeWidget() #0
			self.commitInfo.layout.addWidget(self.commitList,3,0,3,3)
			self.commitList.setHeaderLabels([commitid])
			self.commitList.itemDoubleClicked.connect(self.generateCommitScript)
			self.commitList.setContextMenuPolicy(QtCore.Qt.CustomContextMenu)
			self.commitList.customContextMenuRequested.connect(self.openCommitDetailsMenu)
			

			self.commitList.clear()
			
			trViewObjects = treeModel()
			trViewObjects.generateView(self.commitList, self.dataBaseCommits)

			globalvars.openedCommitTabText.append(self.dataid)
			globalvars.openedCommitTab.append(self.commitInfo)

		objIndex = globalvars.openedCommitTabText.index(commitid)
		self.fileParentTab.setCurrentIndex((4 + objIndex))

	def initData(self):
		index = self.fileParentTab.currentIndex()
		curr_tab = self.fileParentTab.currentWidget()
		line_edit = curr_tab.findChildren(QtWidgets.QLineEdit)
		tree = curr_tab.findChildren(QtWidgets.QTreeWidget)
		plaintext = curr_tab.findChildren(QtWidgets.QPlainTextEdit)
		buttons = curr_tab.findChildren(QtWidgets.QPushButton)
		
		if len(line_edit) > 0 and index not in range(3):
			self.txtCommitID = line_edit[0]
			self.txtCommitFilter = line_edit[1]

			self.commitList = tree[0]
			self.txtCommitMessage = plaintext[0]

			if len(buttons) == 3:
				self.btnOpenServer = buttons[0]
				self.btnCommitMerge = buttons[1]
				self.btnPatch = buttons[2]


	def filterCommitObjects(self, mode):
		self.value = self.txtCommitFilter.text()

		if mode  == "viewcommit":
			self.dataBaseCommits = getCommitDetails(self.dataid)

		if mode  == "viewshelve":
			self.dataBaseCommits = getSheveDetails(self.dataid)

		self.commitList.clear()
		trViewObjects = treeModel()
		trViewObjects.generateView(self.commitList, self.dataBaseCommits, self.value)

	def generateCommitScript(self):
		print("Viewing script info")
		if self.commitList.selectedIndexes() == []:
			item = self.commitList.currentItem()
			itemText = item.text(0)

			dbObjType = item.parent()
			dbObjTypeText = dbObjType.text(0)

			database = dbObjType.parent()
			databaseText = database.text(0)

			objScript = generateCommitScript(None, databaseText, dbObjTypeText, itemText, self.dataid)

			self.versionList.clear() #clear items first
			self.lstEdited.document().setPlainText(objScript);

	def createPatch(self):
		print("Selecting folder for patch")
		try:
			folder = str(QtWidgets.QFileDialog.getExistingDirectory(self, "Select Directory"))

			if folder != "":
				query = get_scripts_by_commit(self.txtCommitID.text())
				conn = pyodbc.connect(globalvars.connString, autocommit=True)
				cursor = conn.cursor()
				files = cursor.execute(query)

				for file in files:
					subfolder = str(folder) + "/" + str(file[2]) + "/"

					if not os.path.isdir(subfolder):
						os.makedirs(subfolder)

					log_obj  = open(subfolder + str(file[0]) + ".txt", "w")
					log_obj.write(str(file[1]))
					log_obj.close()


				error_message = "Patch file has been successfully created"
				QtWidgets.QMessageBox.question(globalvars.MainWindow, "Install Scripts", error_message,  QtWidgets.QMessageBox.Ok)

		except Exception as e:
			saveLog(traceback.format_exc())
			print("Error creating Patch file! Please see log file")
			error_message = "Error creating patch file! Please see log file"
			QtWidgets.QMessageBox.question(globalvars.MainWindow, "Install Scripts", error_message,  QtWidgets.QMessageBox.Ok)

	def removeObj(self):
		print("Remove item")
		# if self.objListTab.selectedIndexes() == []:
		# 	item = self.objListTab.currentItem()
			# itemText = item.text(0)

			# dbObjType = item.parent()
			# dbObjTypeText = dbObjType.text(0)

			# database = dbObjType.parent()
			# databaseText = database.text(0)
			#rowId = item.data(QtCore.Qt.UserRole,0)
		arr_id = self.getAllChildren('select')

		rowId = ",".join(arr_id)

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

			getUserObject()


	def compareShelfToLates(self):
		print("Comparing to latest version")
		if self.commitList.selectedIndexes() == []:
			item = self.commitList.currentItem()
			itemText = item.text(0)

			dbObjType = item.parent()
			dbObjTypeText = dbObjType.text(0)

			database = dbObjType.parent()
			databaseText = database.text(0)

			downloadToCompare(globalvars.username, databaseText, dbObjTypeText, itemText, databaseText, dbObjTypeText, itemText, 'compareShelfLatest', self.txtCommitID.text())

			getUserObject()

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

			objName = ".".join([databaseText, itemText])

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
			self.contParentTab.setTabText(0, objName)


if __name__ == '__main__':
	app = QtWidgets.QApplication(sys.argv)
	# creating main window
	mw = MainWindow()
	mw.show()

	conn = ConnectionWindow()

	sett = SettingsWindow()

	compare = CompareOther()

	about = AboutWindow()

	compHist = CompileHistory()

	mw.checkUpdates()
	
	sys.exit(app.exec_())