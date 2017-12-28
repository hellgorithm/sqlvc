CREATE PROCEDURE getScriptByVersions @database varchar(max), @objType varchar(max), @objName varchar(max)
AS
BEGIN
	-- SET NOCOUNT ON added to prevent extra result sets from
	-- interfering with SELECT statements.
	SET NOCOUNT ON;

    select EventDDL, LoginName, DatabaseName,SchemaName,ObjectName, EventDate, RowID, ObjectType from [SQLVC].[dbo].[DDLEvents] where
		DatabaseName=@database 
		and ObjectType=@objType 
		and SchemaName + '.' + ObjectName=@objName order by RowID desc
END
GO
