CREATE PROCEDURE getLatestScriptByRowId @rowId int
AS
BEGIN
	-- SET NOCOUNT ON added to prevent extra result sets from
	-- interfering with SELECT statements.
	SET NOCOUNT ON;

    -- Insert statements for procedure here
	select top 1 EventDDL from [SQLVC].[dbo].[DDLEvents] where RowID=@rowId
END
