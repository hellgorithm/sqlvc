import globalvars
from PyQt5 import QtCore, QtWidgets


class treeModel():
    def __init__(self):
        print("Setting up models")

    def generateView(self, tw, dat):

        database = ""
        objectType = ""
        obj = ""

        #widgets
        db = None
        otype = None
        dbObj = None

        server = QtWidgets.QTreeWidgetItem(tw)
        server.setText(0, globalvars.server.upper())
        server.setExpanded(True)

        for row in dat:
            #set database
            rdatabase = str(row[1])
            if database != rdatabase:

                database = rdatabase
                objectType = ""

                db = QtWidgets.QTreeWidgetItem(server)
                db.setText(0, str(database))
                db.setExpanded(True)
                #db.setIcon(0,QIcon("your icon path or file name "));

            #set db object type
            # print(database + " == " + str(row[1]))
            # print(objectType + " == " + str(row[5]))
            robjectType = str(row[5])
            if objectType != robjectType and database == str(row[1]):
                
                objectType = robjectType
                obj = ""

                otype = QtWidgets.QTreeWidgetItem(db)
                otype.setText(0, objectType)
                otype.setExpanded(True)

            #set db objects
            rdbObjects = str(row[2] + "." + row[3])
            if obj != rdbObjects:

                obj = rdbObjects

                dbObj = QtWidgets.QTreeWidgetItem(otype)
                dbObj.setText(0, obj)
                dbObj.setExpanded(True)
                dbObj.setCheckState(0,QtCore.Qt.Unchecked)
                dbObj.setFlags(QtCore.Qt.ItemIsUserCheckable | QtCore.Qt.ItemIsEnabled)
                dbObj.setData(QtCore.Qt.UserRole, 0, row[0])

            # for db in databases:
            #     dbObj = QtWidgets.QTreeWidgetItem(server)
            #     dbObj.setText(0, db)
            #     dbObj.setExpanded(True)

            #     for schemaObj in ddl:
            #         schema = QtWidgets.QTreeWidgetItem(dbObj)
            #         schema.setText(0, schemaObj)
            #         schema.setExpanded(True)

            #         for editables in dbo:
            #             edit = QtWidgets.QTreeWidgetItem(schema)
            #             edit.setText(0, editables)
            #             edit.setExpanded(True)
            #             edit.setCheckState(0,QtCore.Qt.Unchecked)
            #             edit.setFlags(QtCore.Qt.ItemIsUserCheckable | QtCore.Qt.ItemIsEnabled)

    

