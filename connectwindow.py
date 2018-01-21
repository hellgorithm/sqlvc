import globalvars
import sys, os, getpass, platform
from PyQt5 import QtWidgets, QtGui, QtCore
from functions import *
from os.path import expanduser
import traceback

class ConnectionWindow(QtWidgets.QMainWindow):
	def __init__(self, parent=None):
		super(ConnectionWindow,self).__init__()

		#initialize window
		self.layout = ConnectLayout(parent=self)
		self.setWindowModality(QtCore.Qt.ApplicationModal)
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

	def darkMode(self):
		if globalvars.darkmode:
			self.setStyleSheet("""background-color:#424242;color:#f4f4f4;""");

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
		self.txtUserName.returnPressed.connect(lambda : OpenConnection(self))

		labelPass = QtWidgets.QLabel(self)
		labelPass.setText("Password")
		grid_layout.addWidget(labelPass, 8, 0, 1, 3)

		self.txtPassword = QtWidgets.QLineEdit(self)
		self.txtPassword.setEchoMode(QtWidgets.QLineEdit.Password)
		self.txtPassword.setEnabled(False)
		self.txtPassword.returnPressed.connect(lambda : OpenConnection(self))
		grid_layout.addWidget(self.txtPassword, 9, 0, 1, 3)

		self.chkRemember = QtWidgets.QCheckBox("Remeber password")
		grid_layout.addWidget(self.chkRemember, 10, 0, 1, 3)

		self.btnOpen = QtWidgets.QPushButton('Open')
		grid_layout.addWidget(self.btnOpen, 11, 1)
		self.btnOpen.clicked.connect(lambda : OpenConnection(self))

		self.btnCancel = QtWidgets.QPushButton('Cancel')
		grid_layout.addWidget(self.btnCancel, 11, 2)
		self.btnCancel.clicked.connect(parent.close)

		self.setDisplayUser(False)

	def setButtonFunction(self):
		if globalvars.connectionMode == 'connectserver':
			self.btnOpen.disconnect()
			self.btnOpen.clicked.connect(lambda : OpenConnection(self))
		elif globalvars.connectionMode == 'mergeserver':
			self.btnOpen.disconnect()
			self.btnOpen.clicked.connect(lambda : OpenConnectionMerge(self))

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

		if platform.system() == "Windows":
			domain = os.environ['userdomain']
		elif platform.system() == "Darwin":
			domain = platform.node()
		else:
			domain = platform.node()
		

		if not display:
			self.txtUserName.setText(domain + "\\" + user)
		else:
			self.txtUserName.setText("")

		self.txtPassword.setText("")



		
		# user = getpass.getuser()

		# if platform.system() == "Windows":
		# 	domain = os.environ['userdomain']
		# elif platform.system() == "Darwin":
		# 	domain = platform.node()
		# else:
		# 	domain = platform.node()

		# if not display:
		# 	self.txtUserName.setText(domain + "\\" + user)
		# else:
		# 	self.txtUserName.setText("")