import globalvars
from PyQt5 import QtWidgets, QtGui, QtCore
import traceback
from functions import *

class CompareOther(QtWidgets.QMainWindow): #compare selection for other version and changeset
	def __init__(self, parent=None):
		super(CompareOther,self).__init__()

		self.layout = CompareLayout(parent=self)
		self.setWindowTitle("Settings")
		self.setWindowIcon(QtGui.QIcon('icons/sqlvc-icon.png'))
		self.setCentralWidget(self.layout)
		self.resize(500, 500)
		#self.setWindowFlags(self.windowFlags() & ~QtCore.Qt.WindowStaysOnTopHint)
		self.center()
		globalvars.compareObj = self

	def center(self):
		frameGm = self.frameGeometry()
		screen = QtWidgets.QApplication.desktop().screenNumber(QtWidgets.QApplication.desktop().cursor().pos())
		centerPoint = QtWidgets.QApplication.desktop().screenGeometry(screen).center()
		frameGm.moveCenter(centerPoint)
		self.move(frameGm.topLeft())

	def darkMode(self):
		if globalvars.darkmode:
			self.setStyleSheet("""background-color:#424242;color:#f4f4f4;""");
			styleSheet = """
				QTreeView {
				    alternate-background-color: #605e5e;
				    background: #424242;
				}
				"""
			self.layout.lstCompareObj.setStyleSheet(styleSheet)

class CompareLayout(QtWidgets.QWidget):

	ROW_ID, DATE, USER, OBJ_DATABASE, OBJ_SCHEMA, OBJ_NAME, OBJ_TYPE  = range(7) 
	CROW_ID, COMMIT_ID, COMMIT_USER, COMMIT_MESSAGE, COMMIT_DATE, COMMIT_DB, COMMIT_OBJTYPE, COMMIT_OBJNAME = range(8) 
	MODE = None

	def __init__(self, parent=None):
		super(CompareLayout, self).__init__()
		grid_layout = QtWidgets.QGridLayout(self)

		self.lstCompareObj = QtWidgets.QTreeView(self)
		self.lstCompareObj.setEditTriggers(QtWidgets.QAbstractItemView.NoEditTriggers)
		self.lstCompareObj.setRootIsDecorated(False)
		self.lstCompareObj.setAlternatingRowColors(True)
		self.lstCompareObj.doubleClicked.connect(self.compareObjectTo)


		grid_layout.addWidget(self.lstCompareObj, 1, 0, 1, 2)

	def compareObjectTo(self):
	# 	index = self.lstCompareObj.currentIndex()
	# 	item = self.lstCompareModel.data(index)
		if globalvars.compareMode == "compareversion":

			index = self.lstCompareObj.selectedIndexes()
			item = self.lstCompareModel.data(index[0])
			db = self.lstCompareModel.data(index[3])
			objType = self.lstCompareModel.data(index[6])
			objName = self.lstCompareModel.data(index[4]) + '.' + self.lstCompareModel.data(index[5])
			
			globalvars.compareObj.hide()
			
			downloadToCompare(globalvars.username, '', '', objName, db, objType, objName, 'compareversion', item)

		elif globalvars.compareMode == "comparecommit":

			index = self.lstCompareObj.selectedIndexes()
			item = self.lstCompareModel.data(index[0])

			commitId = self.lstCompareModel.data(index[1])
			db = self.lstCompareModel.data(index[5])
			objType = self.lstCompareModel.data(index[6])
			objName = self.lstCompareModel.data(index[7])
			
			globalvars.compareObj.hide()
			
			downloadToCompare(globalvars.username, db, objType, objName, db, objType, objName, 'comparecommit', commitId)

		elif globalvars.compareMode == "comparecommit2":

			index = self.lstCompareObj.selectedIndexes()
			item = self.lstCompareModel.data(index[0])

			commitId = self.lstCompareModel.data(index[1])
			db = self.lstCompareModel.data(index[5])
			objType = self.lstCompareModel.data(index[6])
			objName = self.lstCompareModel.data(index[7])
			
			globalvars.compareObj.hide()
			
			downloadToCompare(globalvars.username, db, objType, objName, db, objType, objName, 'comparecommit2', commitId, globalvars.commit1)




	def createCompareModel(self,parent,mode = None):
		
		self.MODE = mode

		if mode == 'version':
			model = QtGui.QStandardItemModel(0, 7, parent)
			model.setHeaderData(self.ROW_ID, QtCore.Qt.Horizontal, "ID")
			model.setHeaderData(self.OBJ_DATABASE, QtCore.Qt.Horizontal, "Database")
			model.setHeaderData(self.OBJ_SCHEMA, QtCore.Qt.Horizontal, "Schema")
			model.setHeaderData(self.OBJ_NAME, QtCore.Qt.Horizontal, "Object Name")
			model.setHeaderData(self.OBJ_TYPE, QtCore.Qt.Horizontal, "Object Type")
			model.setHeaderData(self.USER, QtCore.Qt.Horizontal, "Login Name")
			model.setHeaderData(self.DATE, QtCore.Qt.Horizontal, "Date")

		if mode == 'commit':
			model = QtGui.QStandardItemModel(0, 8, parent)
			model.setHeaderData(self.CROW_ID, QtCore.Qt.Horizontal, "ID")
			model.setHeaderData(self.COMMIT_ID, QtCore.Qt.Horizontal, "Commit ID")
			model.setHeaderData(self.COMMIT_USER, QtCore.Qt.Horizontal, "Commit User")
			model.setHeaderData(self.COMMIT_MESSAGE, QtCore.Qt.Horizontal, "Commit Message")
			model.setHeaderData(self.COMMIT_DB, QtCore.Qt.Horizontal, "Database")
			model.setHeaderData(self.COMMIT_OBJTYPE, QtCore.Qt.Horizontal, "Object Type")
			model.setHeaderData(self.COMMIT_OBJNAME, QtCore.Qt.Horizontal, "Object Name")
			model.setHeaderData(self.COMMIT_DATE, QtCore.Qt.Horizontal, "Commit Date")

		return model

	def addCompare(self,model, rowid, database, schema, objName, objType, user, date):
		model.insertRow(0)
		model.setData(model.index(0, self.OBJ_DATABASE), database)
		model.setData(model.index(0, self.OBJ_SCHEMA), schema)
		model.setData(model.index(0, self.OBJ_NAME), objName)
		model.setData(model.index(0, self.OBJ_TYPE), objType)
		model.setData(model.index(0, self.USER), user)
		model.setData(model.index(0, self.DATE), date)
		model.setData(model.index(0, self.ROW_ID), rowid)

	def addCommit(self,model, cid, commitId, user, message, date, database, objType, objName):
		model.insertRow(0)
		model.setData(model.index(0, self.CROW_ID), cid)
		model.setData(model.index(0, self.COMMIT_ID), commitId)
		model.setData(model.index(0, self.COMMIT_USER), user)
		model.setData(model.index(0, self.COMMIT_MESSAGE), message)
		model.setData(model.index(0, self.COMMIT_DB), database)
		model.setData(model.index(0, self.COMMIT_OBJTYPE), objType)
		model.setData(model.index(0, self.COMMIT_OBJNAME), objName)
		model.setData(model.index(0, self.COMMIT_DATE), date)

	def compareToOtherVersions(self):	
		print("Comparing to other version")

		self.lstCompareModel = self.createCompareModel(self, 'version')
		self.lstCompareObj.setModel(self.lstCompareModel)

		if globalvars.objListTab.selectedIndexes() == []:
			item = globalvars.objListTab.currentItem()
			itemText = item.text(0)

			dbObjType = item.parent()
			dbObjTypeText = dbObjType.text(0)

			database = dbObjType.parent()
			databaseText = database.text(0)

			versionList = generateVersionList(databaseText, dbObjTypeText, itemText)

			for version in reversed(versionList):
				self.addCompare(self.lstCompareModel, version[6],version[2],version[3],version[4],version[7], version[1],str(version[5]))


		#self.lstCompareObj.setColumnHidden(0, True)


	def compareToOtherCommits(self, objTree):
		self.lstCompareModel = self.createCompareModel(self, 'commit')
		self.lstCompareObj.setModel(self.lstCompareModel)

		if objTree.selectedIndexes() == []:
			item = objTree.currentItem()
			itemText = item.text(0)

			dbObjType = item.parent()
			dbObjTypeText = dbObjType.text(0)

			database = dbObjType.parent()
			databaseText = database.text(0)

			commitList = generateCommitListPerItem(databaseText, dbObjTypeText, itemText)

			for commit in reversed(commitList):
				cid = commit[1] + '-' + str(commit[0])
				self.addCommit(self.lstCompareModel, str(commit[0]), cid, commit[2], commit[4], str(commit[3]), databaseText, dbObjTypeText, itemText)

class CompileHistory(QtWidgets.QMainWindow):
	def __init__(self, parent=None):
		super(CompileHistory,self).__init__()

		self.layout = CompileLayout(parent=self)
		self.setWindowTitle("Compile Table History")
		self.setWindowIcon(QtGui.QIcon('icons/sqlvc-icon.png'))
		self.setCentralWidget(self.layout)
		self.resize(700, 500)
		#self.setWindowFlags(self.windowFlags() & ~QtCore.Qt.WindowStaysOnTopHint)
		self.center()
		globalvars.compileHistory = self

	def center(self):
		frameGm = self.frameGeometry()
		screen = QtWidgets.QApplication.desktop().screenNumber(QtWidgets.QApplication.desktop().cursor().pos())
		centerPoint = QtWidgets.QApplication.desktop().screenGeometry(screen).center()
		frameGm.moveCenter(centerPoint)
		self.move(frameGm.topLeft())

class CompileLayout(QtWidgets.QWidget):
	HISTORY_DESC = 0
	COMPILE_ID = ""
	DATABASE = ""
	OBJTYPE = ""
	DBO = ""
	OBJNAME = ""

	def __init__(self, parent=None):
		super(CompileLayout, self).__init__()
		grid_layout = QtWidgets.QGridLayout(self)

		self.lstCompileObj = QtWidgets.QTreeView(self)
		self.lstCompileObj.setEditTriggers(QtWidgets.QAbstractItemView.NoEditTriggers)
		self.lstCompileObj.setRootIsDecorated(False)
		self.lstCompileObj.setAlternatingRowColors(True)

		self.compileDocPreview = QtWidgets.QPlainTextEdit(self)

		self.btnApply = QtWidgets.QPushButton("Apply")
		self.btnApply.clicked.connect(self.applyCompiledData)

		self.btnClose = QtWidgets.QPushButton("Close")
		self.btnClose.clicked.connect(self.hideMe)


		grid_layout.addWidget(self.lstCompileObj, 1, 0, 1, 3)
		grid_layout.addWidget(self.compileDocPreview, 1, 4, 1, 3)
		grid_layout.addWidget(self.btnApply, 2, 5, 1, 1)
		grid_layout.addWidget(self.btnClose, 2, 6, 1, 1)

		self.lstCompileObjModel = self.createCompileModel(self)
		self.lstCompileObjModel.itemChanged.connect(self.on_item_changed)



		self.lstCompileObj.setModel(self.lstCompileObjModel)
		#self.lstCompileObj.clicked.connect(self.checkUncheck)

	def hideMe(self):
		globalvars.compileHistory.hide()

	def setEditData(self, versions):
		self.lstCompileObjModel.removeRows(0, self.lstCompileObjModel.rowCount())

		for version in versions:
			desc = version[2] + '.' + version[3] + '.' + version[4] + ' modified last ' + str(version[5]) + ' by ' + version[1]
			self.addCompileData(self.lstCompileObjModel, version[6], desc)
			self.DATABASE = version[2]
			self.OBJTYPE = version[7]
			self.DBO = version[3]
			self.OBJNAME = version[4]

	def on_item_changed(self, item):
		i = 0
		checked = 0
		arrRowID = []
		compiled_dat = ""

		while self.lstCompileObjModel.item(i):
			if self.lstCompileObjModel.item(i).checkState() == QtCore.Qt.Checked:
				arrRowID.append(str(self.lstCompileObjModel.item(i).data(QtCore.Qt.UserRole)))
				checked += 1
			i += 1

		if checked > 0:
			self.COMPILE_ID = ",".join(arrRowID)

			compile_dataset = getCompiledScripts(self.COMPILE_ID)

			for com in compile_dataset:
				compiled_dat = compiled_dat + com[0] + "\n\n"

		self.compileDocPreview.document().setPlainText(compiled_dat)

	def createCompileModel(self, parent):
		model = QtGui.QStandardItemModel(0, 1, parent)
		model.setHeaderData(self.HISTORY_DESC, QtCore.Qt.Horizontal, "Edit History")

		return model

	def addCompileData(self, model, hId, historyDesc):
		item = QtGui.QStandardItem(historyDesc)
		# check = QtCore.Qt.Checked
		# item.setCheckState(check)
		item.setCheckable(True)
		item.setData(hId, QtCore.Qt.UserRole)
		model.appendRow(item)

	def clean(self):
		self.compileDocPreview.document().setPlainText("")


	def applyCompiledData(self):
		try:
			eventDDL = self.compileDocPreview.toPlainText()
			if globalvars.engine == "Microsoft SQL Server":
				ddl = eventDDL.replace("'", "''")
				query = saveCompiledScript(ddl, self.DATABASE, self.DBO, self.OBJNAME, self.OBJTYPE)
				
				conn = pyodbc.connect(globalvars.connString, autocommit=True)
				cursor = conn.cursor()
				commits = cursor.execute(query)
			
			message = "Compiled script for commit successfully created"
			reply = QtWidgets.QMessageBox.question(globalvars.MainWindow, "Compile Scripts", message,  QtWidgets.QMessageBox.Ok)

			self.clean()
			globalvars.compileHistory.hide()

		except Exception as e:
			saveLog(traceback.format_exc())
			error_message = "Error compiling scripts. Please see log file for details."
			reply = QtWidgets.QMessageBox.question(globalvars.MainWindow, "Compile Scripts", error_message,  QtWidgets.QMessageBox.Ok)



