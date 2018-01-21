def get_latest_script_by_user(user, database, objectType, ObjectName):
	return """SELECT top 1 EventDDL from [SQLVC].[dbo].[DDLEvents] where (LoginName='""" + str(user) + """' or '""" + str(user) + """'='')
							and DatabaseName='""" + str(database) + """' and ObjectType='""" + str(objectType) + """' 
							and SchemaName + '.' + ObjectName='""" + str(ObjectName) + """' order by RowID desc"""

def get_latest_script(objectType, objectName):
	#return """select text, type from sysobjects o join syscomments c on c.id = o.id where o.name = '"""+objectName+"""' and o.type= '"""+str(objectType)+"""'"""
	return """select mod.definition, o.type from sys.sql_modules mod join sysobjects o on mod.object_id=o.id where OBJECT_NAME(OBJECT_ID) = '"""+objectName+"""' and o.type='"""+objectType+"""'"""


def get_latest_script_v2(user, database, objectType, objectName):
	return """  declare @vsSQL varchar(8000)
				declare @vsTableName varchar(50)
				select @vsTableName = '"""+objectName+"""'

				select @vsSQL = 'CREATE TABLE ' + @vsTableName + char(10) + '(' + char(10)

				select @vsSQL = @vsSQL + ' ' + sc.Name + ' ' +
				st.Name +
				case when st.Name in ('varchar','varchar','char','nchar') then '(' + cast(sc.Length as varchar) + ') ' else ' ' end +
				case when sc.IsNullable = 1 then 'NULL' else 'NOT NULL' end + ',' + char(10)
				from sysobjects so
				join syscolumns sc on sc.id = so.id
				join systypes st on st.xusertype = sc.xusertype
				where so.name = @vsTableName
				order by
				sc.ColID

				select substring(@vsSQL,1,len(@vsSQL) - 2) + char(10) + ')'"""


def get_workspace_script_by_user(user, database, objectType, ObjectName):
	return """SELECT top 1 RowID from [SQLVC].[dbo].[UserWorkspace] where (LoginName='""" + str(user) + """' or '""" + str(user) + """'='')
							and DatabaseName='""" + str(database) + """' and ObjectType='""" + str(objectType) + """' 
							and SchemaName + '.' + ObjectName='""" + str(ObjectName) + """' order by RowID desc"""

def get_latest_script_by_rowid(rowid):
	return """SELECT top 1 EventDDL from [SQLVC].[dbo].[DDLEvents] where RowID='""" + str(rowid) + """'"""


def get_latest_script_by_commit(database, objectType, objectName, commitid):
	return """SELECT ObjectDDL from [SQLVC].[dbo].[Commits_dtl] where CommitID='""" + str(commitid) + """' and DatabaseName='""" + str(database) + """' and ObjectType='""" + str(objectType) + """' and (SchemaName + '.' + ObjectName)='""" + str(objectName) + """'"""


def get_shelfitem_by_rowid(database, objectType, objectName, shelveid):
	return """SELECT ObjectDDL from [SQLVC].[dbo].[Shelve_dtl] where ShelveID='""" + str(shelveid) + """' and DatabaseName='""" + str(database) + """' and ObjectType='""" + str(objectType) + """' and (SchemaName + '.' + ObjectName)='""" + str(objectName) + """'"""


def get_scripts_by_commit(commitid):
	return """SELECT ObjectName, ObjectDDL, ObjectType from [SQLVC].[dbo].[Commits_dtl] where CommitID='""" + str(commitid) + """'"""

def get_scripts_apply_shelve(shelveid, database, objectType, objectName):
	return """insert into dbo.UserWorkspace(DatabaseName, SchemaName, ObjectName, LoginName, ObjectType)
			select DatabaseName, SchemaName, ObjectName, LoginName, ObjectType from Shelve_dtl where ShelveID='"""+shelveid+"""' and DatabaseName='"""+database+"""' and ObjectType='"""+objectType+"""' and (SchemaName + '.' + ObjectName)='"""+objectName+"""'"""

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

def save_shelve_detail(shelveID, rowId):
	return """insert into [SQLVC].[dbo].[Shelve_dtl](ShelveID, DatabaseName, SchemaName, ObjectName, LoginName, ObjectType, ObjectDDL)
								select '""" + shelveID + """',DatabaseName, SchemaName, ObjectName, LoginName, ObjectType,(select top 1 EventDDL from [dbo].[DDLEvents] 
								where DatabaseName=ws.DatabaseName and SchemaName=ws.SchemaName and ObjectType=ws.ObjectType and ObjectName=ws.ObjectName 
								order by RowID desc) from [SQLVC].[dbo].[UserWorkspace] ws where RowId in (""" + rowId + """);"""

def saveCompiledScript(EventDDL, DatabaseName, SchemaName, ObjectName, ObjectType):
	return """insert into [SQLVC].[dbo].[DDLEvents] (EventType, EventDDL, DatabaseName, SchemaName, ObjectName, ObjectType, HostName, IPAddress, ProgramName, LoginName, EventDate) 
			values ('COMPILE_TABLE', '"""+str(EventDDL)+"""','"""+DatabaseName+"""','"""+SchemaName+"""','"""+ObjectName+"""','"""+ObjectType+"""',HOST_NAME(),(SELECT TOP 1 client_net_address FROM sys.dm_exec_connections WHERE session_id = @@SPID),'SQLVC',SUSER_SNAME(),GETDATE())"""


def checkConflict(rowId):
	return """select case when (select top 1 LoginName from [dbo].[DDLEvents] 
								where DatabaseName=ws.DatabaseName and SchemaName=ws.SchemaName and ObjectType=ws.ObjectType and ObjectName=ws.ObjectName 
								and EventType not like '%TABLE%' or EventType = 'COMPILE_TABLE'
								order by RowID desc) = ws.LoginName and (select top 1 (case when EventType not like '%TABLE%' or EventType = 'COMPILE_TABLE' then '1' else '0' end) from [dbo].[DDLEvents] 
								where DatabaseName=ws.DatabaseName and SchemaName=ws.SchemaName and ObjectType=ws.ObjectType and ObjectName=ws.ObjectName 
								order by RowID desc) = '1'
								then 'ok' else 'conflict' end,*
								from [dbo].[UserWorkspace] ws where RowId in (""" + rowId + """)"""

def getShelvedDetails(shelveid, userid = ''):
	return "select RowID, DatabaseName, SchemaName, ObjectName, LoginName, ObjectType from [SQLVC].[dbo].[Shelve_dtl] where ShelveID='" + shelveid + "' and LoginName='"+userid+"' order by DatabaseName, ObjectType, ObjectName"