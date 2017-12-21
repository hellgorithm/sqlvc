import globalvars
import sys, os, getpass, platform
from PyQt5 import QtWidgets, QtGui, QtCore
import xml.etree.cElementTree as ET
from treeModel import treeModel
from functions import *
from os.path import expanduser

#window
from comparewindow import *
from settingswindow import *
from connectwindow import *

class MainWindow(QtWidgets.QMainWindow):
	def __init__(self, parent=None):
		super(MainWindow,self).__init__()

		#initialize window
		self.layout = Layout(parent=self)
		self.setWindowTitle("SQLVC")
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

		open_log = QtWidgets.QAction('Open &Logs', self)
		file_menu.addAction(open_log)
		open_log.triggered.connect(self.openLogFolder)
		open_log.setShortcut(QtGui.QKeySequence("Ctrl+L"))

		preference_action = QtWidgets.QAction('&Preferences', self)
		edit_menu.addAction(preference_action)
		edit_menu.triggered.connect(self.openPreference)
		preference_action.setShortcut(QtGui.QKeySequence("Ctrl+P"))

		close_action = QtWidgets.QAction('&Quit', self)
		file_menu.addAction(close_action)
		close_action.setShortcut(QtGui.QKeySequence("Ctrl+Q"))

		about_action = QtWidgets.QAction('&About', self)
		help_menu.addAction(about_action)
		about_action.setShortcut(QtGui.QKeySequence("Ctrl+A"))

		# use `connect` method to bind signals to desired behavior
		close_action.triggered.connect(self.close_windows)

	def openPreference(self):
		exePath = sett.layout.readExePath()
		sett.layout.txtExePath.setText(exePath)
		sett.show()

	def close_windows(self):
		self.close()

	def setSQLWindowTitle(self):
		title = "SQLVC - " + globalvars.server + "[" + globalvars.username + "]"
		self.setWindowTitle(title)


	def addConnection(self):
		home = expanduser("~")
		homeConfigPath = home + "/sqlvc/sqlvc-config.xml"
		readConnConfiguration(homeConfigPath, conn)
		conn.show()


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

		fileParentTab = QtWidgets.QTabWidget()
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

		fileParentTab.addTab(fileList, "Objects")
		fileParentTab.addTab(changesetListTab, "Commits")

		self.contParentTab.addTab(self.contentTab,"Details")
		self.contParentTab.addTab(versionTab,"Versions")
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

		changesetListTab.layout.addWidget(self.lstCommits, 0,0,1,1)
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

		grid_layout.addWidget(self.contParentTab, 1, 0, 1, 2)
		grid_layout.addWidget(fileParentTab, 1, 2, 1, 2) #row, column, height, width
		# self.scriptDetails = QtWidgets.QListWidget(self)
		# tab_layout.addWidget(self.scriptDetails, 0, 2, 1, 2)

		# self.detailsTab = QtWidgets.QWidget()
		# grid_layout.addTab(tab_layout, 1, 4, 1, 2)
		#en tab

		# self.save_button = QtWidgets.QPushButton('Save')
		# self.clear_button = QtWidgets.QPushButton('Clear')
		# self.open_button = QtWidgets.QPushButton('Open')
		# self.quit_button = QtWidgets.QPushButton('Quit')

		# grid_layout.addWidget(self.save_button, 2, 0)
		# grid_layout.addWidget(self.clear_button, 2, 1)
		# grid_layout.addWidget(self.open_button, 2, 2)
		# grid_layout.addWidget(self.quit_button, 2, 3)
		globalvars.MainWindow = self

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

			compareVersion = menu.addAction(self.tr("Compare to other versions"))
			compareVersion.triggered.connect(self.compareOtherVersion)

			compareCommit = menu.addAction(self.tr("Compare to other commits"))
			compareCommit.triggered.connect(self.compareOtherCommit)

			menu.addAction(self.tr("Revert to previous state"))
			menu.addAction(self.tr("Include/Exclude"))

			menu.exec_(self.objListTab.viewport().mapToGlobal(position))

	def compareOtherVersion(self):
		globalvars.compareObj.layout.compareToOtherVersions()
		globalvars.compareObj.setWindowFlags(globalvars.compareObj.windowFlags() | QtCore.Qt.WindowStaysOnTopHint)
		compare.show()
		#globalvars.compareObj.

	def compareOtherCommit(self):
		globalvars.compareObj.layout.compareToOtherCommits()
		compare.show()

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
	
	sys.exit(app.exec_())