import os

engine = "Microsoft SQL Server"
server = None
database = None
username = None
password = None
authType = None
connString = None
connTest = None
databaseEdits = {}
objListTab = None
sett = None
compareObj = None
masterPassword = "P@ssw0rd"

openedCommitTab = []
openedCommitTabText = []
openedDetailsTab = []
openedDetailsTabID = []

version = "alpha 1.6"
darkmode = False
connectionMode = 'connectserver'
serverTypeMerge = None
serverMerge = None
usernameMerge = None
passwordMerge = None
authTypeMerge = None
icon = os.path.join("icons","sqlvc-icon.png")
version_url = "http://hellgorithm.github.io/sqlvc_version.txt"
dl_url = "https://github.com/hellgorithm/sqlvc#binary"

#ENGINE MSSSQL
DBTEST = "master"
DBGIT = "SQLVC"
SQLSERVER = "ODBC Driver 13 for SQL Server"
WORKSPACE_SELECTED = []
