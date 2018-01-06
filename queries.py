def get_latest_script_by_user(user, database, objectType, ObjectName):
	return """SELECT top 1 EventDDL from [SQLVC].[dbo].[DDLEvents] where (LoginName='""" + str(user) + """' or '""" + str(user) + """'='')
							and DatabaseName='""" + str(database) + """' and ObjectType='""" + str(objectType) + """' 
							and SchemaName + '.' + ObjectName='""" + str(ObjectName) + """' order by RowID desc"""

def get_workspace_script_by_user(user, database, objectType, ObjectName):
	return """SELECT top 1 RowID from [SQLVC].[dbo].[UserWorkspace] where (LoginName='""" + str(user) + """' or '""" + str(user) + """'='')
							and DatabaseName='""" + str(database) + """' and ObjectType='""" + str(objectType) + """' 
							and SchemaName + '.' + ObjectName='""" + str(ObjectName) + """' order by RowID desc"""

def get_latest_script_by_rowid(rowid):
	return """SELECT top 1 EventDDL from [SQLVC].[dbo].[DDLEvents] where RowID='""" + str(rowid) + """'"""


def get_latest_script_by_commit(database, objectType, objectName, commitid):
	return """SELECT ObjectDDL from [SQLVC].[dbo].[Commits_dtl] where CommitID='""" + str(commitid) + """' and DatabaseName='""" + str(database) + """' and ObjectType='""" + str(objectType) + """' and (SchemaName + '.' + ObjectName)='""" + str(objectName) + """'"""



def get_script_by_versions(database, objectType, objectName):
	return """select EventDDL, LoginName, DatabaseName,SchemaName,ObjectName, EventDate, RowID, ObjectType from [SQLVC].[dbo].[DDLEvents] where
		DatabaseName='"""+database+"""' 
		and ObjectType='"""+objectType+"""' 
		and SchemaName + '.' + ObjectName='"""+objectName+"""' order by RowID desc"""

def get_script_by_commit_per_item(database, objectType, objectName):
	return """select *, '"""+str(database)+"""' 'database','"""+str(objectType)+"""' 'objectType','"""+str(objectName)+"""' 'objectName' from [dbo].[Commits_hdr] where CommitID + '-' + convert(varchar(100),RowID) in (
					select CommitID from [dbo].[Commits_dtl] where 
						DatabaseName='"""+str(database)+"""' and ObjectType='"""+str(objectType)+"""' 
						and SchemaName + '.' + ObjectName='"""+str(objectName)+"""'
				) order by RowID desc"""

def save_commit_detail(commitID, rowId):
	return """insert into [SQLVC].[dbo].[Commits_dtl](CommitID, DatabaseName, SchemaName, ObjectName, LoginName, ObjectType, ObjectDDL)
								select '""" + commitID + """',DatabaseName, SchemaName, ObjectName, LoginName, ObjectType,(select top 1 EventDDL from [dbo].[DDLEvents] 
								where DatabaseName=ws.DatabaseName and SchemaName=ws.SchemaName and ObjectType=ws.ObjectType and ObjectName=ws.ObjectName 
								order by RowID desc) from [SQLVC].[dbo].[UserWorkspace] ws where RowId in (""" + rowId + """);"""