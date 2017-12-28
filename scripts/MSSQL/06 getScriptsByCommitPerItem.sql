CREATE PROCEDURE getScriptByCommitPerItem  @database varchar(max), @objType varchar(max), @objName varchar(max)
AS
BEGIN

	SET NOCOUNT ON;

    select *, @database 'database',@objType 'objectType',@objName 'objectName' from [dbo].[Commits_hdr] where CommitID in (
		select CommitID from [dbo].[Commits_dtl] where 
			DatabaseName=@database and ObjectType=@objType 
			and SchemaName + '.' + ObjectName=@objName
	) order by RowID desc
END