from PyQt5 import QtCore, QtWidgets


class treeModel():
    def __init__(self):
        print("Setting up models")

    def generateView(self, tw, dat):

        #tests data
        databases = "HuManEDGE|HuManEDGECLIENT".split("|")
        ddl = "Tables|Views|Stored Procedures|Functions".split("|")
        dbo = "hello|world".split("|")

        server = QtWidgets.QTreeWidgetItem(tw)
        server.setText(0, "ZERO-VM\DEV")
        server.setExpanded(True)

        for db in databases:
            dbObj = QtWidgets.QTreeWidgetItem(server)
            dbObj.setText(0, db)
            dbObj.setExpanded(True)

            for schemaObj in ddl:
                schema = QtWidgets.QTreeWidgetItem(dbObj)
                schema.setText(0, schemaObj)
                schema.setExpanded(True)

                for editables in dbo:
                    edit = QtWidgets.QTreeWidgetItem(schema)
                    edit.setText(0, editables)
                    edit.setExpanded(True)
                    edit.setCheckState(0,QtCore.Qt.Unchecked)
                    edit.setFlags(QtCore.Qt.ItemIsUserCheckable | QtCore.Qt.ItemIsEnabled)
