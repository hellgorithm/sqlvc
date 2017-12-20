CREATE PROCEDURE getLatestScriptByUser @user varchar(max), @database varchar(max), @objType varchar(max), @objName varchar(max)
AS
BEGIN

	SET NOCOUNT ON;

    select top 1 EventDDL from [SQLVC].[dbo].[DDLEvents] where (LoginName=@user or @user='')
		and DatabaseName=@database 
		and ObjectType=@objType 
		and SchemaName + '.' + ObjectName=@objName order by RowID desc
END
GO