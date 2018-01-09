import globalvars
from PyQt5 import QtWidgets, QtGui, QtCore
import xml.etree.cElementTree as ET
from functions import *
from os.path import expanduser
import traceback

class AboutWindow(QtWidgets.QMainWindow):
	def __init__(self, parent=None):
		super(AboutWindow,self).__init__()

		self.layout = AboutLayout(parent=self)
		self.setWindowTitle("About SQLVC")
		self.setWindowIcon(QtGui.QIcon('./openmonitor.png'))
		self.setCentralWidget(self.layout)
		self.resize(500, 130)
		self.setFixedSize(self.size())
		self.setWindowFlags(QtCore.Qt.WindowCloseButtonHint | QtCore.Qt.WindowMinimizeButtonHint)
		self.center()
		globalvars.about = self

	def center(self):
		frameGm = self.frameGeometry()
		screen = QtWidgets.QApplication.desktop().screenNumber(QtWidgets.QApplication.desktop().cursor().pos())
		centerPoint = QtWidgets.QApplication.desktop().screenGeometry(screen).center()
		frameGm.moveCenter(centerPoint)
		self.move(frameGm.topLeft())

	def darkMode(self):
		if globalvars.darkmode:
			self.setStyleSheet("""background-color:#424242;color:#f4f4f4;""");

class AboutLayout(QtWidgets.QWidget):
	def __init__(self, parent=None):
		super(AboutLayout, self).__init__()
		grid_layout = QtWidgets.QGridLayout(self)

		labelDiffTool = QtWidgets.QLabel(self)
		labelDiffTool.setText("SQLVC " + globalvars.version +  "\n\nSQLVC Cross platform version control for SQL server. For source code\n visit https://github.com/hellgorithm/sqlvc\n\nDeveloper : Hellgorithm")
		labelDiffTool.setOpenExternalLinks(True)

		grid_layout.addWidget(labelDiffTool, 0, 0, 1, 3)

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

	def darkMode(self):
		if globalvars.darkmode:
			self.setStyleSheet("""background-color:#424242;color:#f4f4f4;""");

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
		globalvars.sett.close()

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
			saveLog(traceback.format_exc())
			error_message = "Error saving config! Please see log file"
			reply = QtWidgets.QMessageBox.question(self, "Error!", error_message,  QtWidgets.QMessageBox.Ok)