import globalvars
import sys, os, getpass, platform
from PyQt5 import QtWidgets, QtGui, QtCore
import xml.etree.cElementTree as ET
from treeModel import treeModel
from functions import *
from os.path import expanduser
import platform


class CompareOther(QtWidgets.QMainWindow): #compare selection for other version and changeset
	def __init__(self, parent=None):
		super(CompareOther,self).__init__()

		self.layout = CompareLayout(parent=self)
		self.setWindowTitle("Settings")
		self.setWindowIcon(QtGui.QIcon('./openmonitor.png'))
		self.setCentralWidget(self.layout)
		self.resize(500, 500)
		# self.setWindowFlags(QtCore.Qt.WindowStaysOnTopHint)
		self.center()
		#globalvars.sett = self

	def center(self):
		frameGm = self.frameGeometry()
		screen = QtWidgets.QApplication.desktop().screenNumber(QtWidgets.QApplication.desktop().cursor().pos())
		centerPoint = QtWidgets.QApplication.desktop().screenGeometry(screen).center()
		frameGm.moveCenter(centerPoint)
		self.move(frameGm.topLeft())

class CompareLayout(QtWidgets.QWidget):

	OBJ_DATABASE, OBJ_SCHEMA, OBJ_NAME, USER, DATE = range(5) 

	def __init__(self, parent=None):
		super(CompareLayout, self).__init__()
		grid_layout = QtWidgets.QGridLayout(self)

		self.lstCompareObj = QtWidgets.QTreeView(self)
		self.lstCompareObj.setRootIsDecorated(False)
		self.lstCompareObj.setAlternatingRowColors(True)

		self.lstCompareModel = self.createCompareModel(self)
		
		self.lstCompareObj.setModel(self.lstCompareModel)

		grid_layout.addWidget(self.lstCompareObj, 1, 0, 1, 2)

	def createCompareModel(self,parent):
		model = QtGui.QStandardItemModel(0, 5, parent)
		model.setHeaderData(self.OBJ_DATABASE, QtCore.Qt.Horizontal, "Database")
		model.setHeaderData(self.OBJ_SCHEMA, QtCore.Qt.Horizontal, "Schema")
		model.setHeaderData(self.OBJ_NAME, QtCore.Qt.Horizontal, "Object Name")
		model.setHeaderData(self.USER, QtCore.Qt.Horizontal, "Login Name")
		model.setHeaderData(self.DATE, QtCore.Qt.Horizontal, "Date")
		return model

	def addCompare(self,model, database, schema, objName, user, date):
		model.insertRow(0)
		model.setData(model.index(0, self.OBJ_DATABASE), database)
		model.setData(model.index(0, self.OBJ_SCHEMA), schema)
		model.setData(model.index(0, self.OBJ_NAME), objName)
		model.setData(model.index(0, self.USER), user)
		model.setData(model.index(0, self.DATE), date)

class SettingsWindow(QtWidgets.QMainWindow):
	def __init__(self, parent=None):
		super(SettingsWindow,self).__init__()

		self.layout = SettingsLayout(parent=self)
		self.setWindowTitle("Settings")
		self.setWindowIcon(QtGui.QIcon('./openmonitor.png'))
		self.setCentralWidget(self.layout)
		self.resize(250, 130)
		# self.setWindowFlags(QtCore.Qt.WindowStaysOnTopHint)
		self.center()
		globalvars.sett = self

	def center(self):
		frameGm = self.frameGeometry()
		screen = QtWidgets.QApplication.desktop().screenNumber(QtWidgets.QApplication.desktop().cursor().pos())
		centerPoint = QtWidgets.QApplication.desktop().screenGeometry(screen).center()
		frameGm.moveCenter(centerPoint)
		self.move(frameGm.topLeft())

class SettingsLayout(QtWidgets.QWidget):
	def __init__(self, parent=None):
		super(SettingsLayout, self).__init__()
		grid_layout = QtWidgets.QGridLayout(self)

		labelDiffTool = QtWidgets.QLabel(self)
		labelDiffTool.setText("Diff Tool")
		grid_layout.addWidget(labelDiffTool, 0, 0, 1, 3)

		self.txtExePath = QtWidgets.QLineEdit(self)
		grid_layout.addWidget(self.txtExePath, 1, 0, 1, 2)

		btnBrowseExe = QtWidgets.QPushButton("Browse")
		grid_layout.addWidget(btnBrowseExe, 1, 2, 1, 1)
		btnBrowseExe.clicked.connect(self.openFileExplorer)

		self.btnSaveExe = QtWidgets.QPushButton("Save")
		grid_layout.addWidget(self.btnSaveExe, 2, 1, 1, 1)
		self.btnSaveExe.clicked.connect(self.saveExePath)

		self.btnCancel = QtWidgets.QPushButton("Cancel")
		grid_layout.addWidget(self.btnCancel, 2, 2, 1, 1)
		self.btnCancel.clicked.connect(self.closeSett)

	def closeSett(self):
		sett.close()

	def openFileExplorer(self):
		difftool = str(QtWidgets.QFileDialog.getOpenFileName(self, "Select Difftool")[0])
		self.txtExePath.setText(difftool)

	def readExePath(self):
		exePath = self.txtExePath.text()
		home = expanduser("~")
		homeConfigPath = home + "/sqlvc/sqlvc-config.xml"

		root = ET.parse(homeConfigPath).getroot()

		tool = root.find('difftool')
		path = ""

		# if tool == None:
		# 	path = ""
		# else:
		# 	path = tool.text

		# self.txtExePath.setText(path)
		if tool == None:
			return ""
		else:
			return tool.text



	def saveExePath(self):
		try:
			exePath = self.txtExePath.text()
			home = expanduser("~")
			homeConfigPath = home + "/sqlvc/sqlvc-config.xml"

			root = ET.parse(homeConfigPath).getroot()

			tool = root.find('difftool')

			if tool == None:
				tool = ET.SubElement(root, "difftool")

			tool.text = str(exePath)


			tree = ET.ElementTree(root)
			tree.write(homeConfigPath)

			success_message = "Successfully saved config file."
			reply = QtWidgets.QMessageBox.question(self, "Success!", success_message,  QtWidgets.QMessageBox.Ok)
		except Exception as e:
			saveLog(e)
			error_message = "Error saving config! Please see log file"
			reply = QtWidgets.QMessageBox.question(self, "Error!", error_message,  QtWidgets.QMessageBox.Ok)

class ConnectionWindow(QtWidgets.QMainWindow):
	def __init__(self, parent=None):
		super(ConnectionWindow,self).__init__()

		#initialize window
		self.layout = ConnectLayout(parent=self)
		self.setWindowTitle("Open Connection")
		self.setWindowIcon(QtGui.QIcon('./openmonitor.png'))
		self.setCentralWidget(self.layout)
		self.resize(250, 130)
		self.setWindowFlags(QtCore.Qt.WindowStaysOnTopHint)
		#self.setGeometry(10, 10, 250, 130)
		self.center()
		self.openUserConfig()

	def openUserConfig(self):
		home = expanduser("~")
		homeConfigPath = home + "/sqlvc/sqlvc-config.xml"

		if os.path.exists(homeConfigPath):
			print("read")
		else:
			saveConfigurations(homeConfigPath)

	def center(self):
		frameGm = self.frameGeometry()
		screen = QtWidgets.QApplication.desktop().screenNumber(QtWidgets.QApplication.desktop().cursor().pos())
		centerPoint = QtWidgets.QApplication.desktop().screenGeometry(screen).center()
		frameGm.moveCenter(centerPoint)
		self.move(frameGm.topLeft())

class ConnectLayout(QtWidgets.QWidget):
	def __init__(self, parent=None):
		super(ConnectLayout, self).__init__()
		# create and set layout to place widgets
		grid_layout = QtWidgets.QGridLayout(self)

		#self.text_box = QtWidgets.QTextEdit(self)
		labelDatabase = QtWidgets.QLabel(self)
		labelDatabase.setText("Database")
		grid_layout.addWidget(labelDatabase, 0, 0, 1, 3)

		self.cmbDbase = QtWidgets.QComboBox(self)       	
		grid_layout.addWidget(self.cmbDbase, 1, 0, 1, 3)
		self.cmbDbase.addItem("Microsoft SQL Server")

		labelEdited = QtWidgets.QLabel(self)
		labelEdited.setText("Server/Instance")
		grid_layout.addWidget(labelEdited, 2, 0, 1, 3)

		self.cmbServers = QtWidgets.QComboBox(self)       	
		grid_layout.addWidget(self.cmbServers, 3, 0, 1, 3)
		self.cmbServers.setEditable(True)
		self.cmbServers.lineEdit().setMaxLength(100)

		self.labelAuthType = QtWidgets.QLabel(self)
		self.labelAuthType.setText("Authentication")
		grid_layout.addWidget(self.labelAuthType, 4, 0, 1, 3)

		self.cmbAuthType = QtWidgets.QComboBox(self)  
		self.cmbAuthType.addItem("Windows Authentication")
		self.cmbAuthType.addItem("SQL Authentication")     	
		grid_layout.addWidget(self.cmbAuthType, 5, 0, 1, 3)
		self.cmbAuthType.currentIndexChanged.connect(self.authChange)

		labelUser = QtWidgets.QLabel(self)
		labelUser.setText("UserName")
		grid_layout.addWidget(labelUser, 6, 0, 1, 3)

		self.txtUserName = QtWidgets.QLineEdit(self)
		grid_layout.addWidget(self.txtUserName, 7, 0, 1, 3)
		self.txtUserName.setEnabled(False)

		labelPass = QtWidgets.QLabel(self)
		labelPass.setText("Password")
		grid_layout.addWidget(labelPass, 8, 0, 1, 3)

		self.txtPassword = QtWidgets.QLineEdit(self)
		self.txtPassword.setEchoMode(QtWidgets.QLineEdit.Password)
		self.txtPassword.setEnabled(False)
		grid_layout.addWidget(self.txtPassword, 9, 0, 1, 3)


		btnOpen = QtWidgets.QPushButton('Open')
		grid_layout.addWidget(btnOpen, 10, 1)
		btnOpen.clicked.connect(lambda : OpenConnection(self))

		self.btnCancel = QtWidgets.QPushButton('Cancel')
		grid_layout.addWidget(self.btnCancel, 10, 2)
		self.btnCancel.clicked.connect(parent.close)

		self.setDisplayUser(False)

	def authChange(self):
		enable = None

		if self.cmbAuthType.currentText() == "Windows Authentication":
			enable = False
		else:
			enable = True

		self.txtUserName.setEnabled(enable)
		self.txtPassword.setEnabled(enable)
		self.setDisplayUser(enable)

	def setDisplayUser(self, display):
		#domain = os.environ['userdnsdomain']
		user = getpass.getuser()
		domain = platform.node()

		if not display:
			self.txtUserName.setText(domain + "\\" + user)
		else:
			self.txtUserName.setText("")

class MainWindow(QtWidgets.QMainWindow):
	def __init__(self, parent=None):
		super(MainWindow,self).__init__()

		#initialize window
		self.layout = Layout(parent=self)
		self.setWindowTitle("SQLGVC")
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

		open_log = QtWidgets.QAction('Open &Logs', self)
		file_menu.addAction(open_log)
		open_log.triggered.connect(self.openLogFolder)

		preference_action = QtWidgets.QAction('&Preferences', self)
		edit_menu.addAction(preference_action)
		edit_menu.triggered.connect(self.openPreference)

		close_action = QtWidgets.QAction('&Quit', self)
		file_menu.addAction(close_action)

		about_action = QtWidgets.QAction('&About', self)
		help_menu.addAction(about_action)

		# use `connect` method to bind signals to desired behavior
		close_action.triggered.connect(self.close_windows)

	def openPreference(self):
		exePath = sett.layout.readExePath()
		sett.layout.txtExePath.setText(exePath)
		sett.show()

	def close_windows(self):
		self.close()


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

			menu.addAction(self.tr("Compare to other commits"))
			menu.addAction(self.tr("Revert to previous state"))
			menu.addAction(self.tr("Include/Exclude"))

			menu.exec_(self.objListTab.viewport().mapToGlobal(position))

	def compareOtherVersion(self):
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