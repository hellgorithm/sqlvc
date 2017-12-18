CREATE TRIGGER [SQLGitEventLogger]
    ON ALL SERVER
    --FOR CREATE_PROCEDURE, ALTER_PROCEDURE, DROP_PROCEDURE
    FOR DDL_DATABASE_LEVEL_EVENTS
AS
BEGIN
   SET NOCOUNT ON;
    DECLARE
        @EventData XML = EVENTDATA();
 
    DECLARE 
        @ip VARCHAR(32) =
        (
            SELECT client_net_address
                FROM sys.dm_exec_connections
                WHERE session_id = @@SPID
        );

    --check if object is already in user's workspace, if not...add one 
    IF NOT EXISTS(SELECT * FROM SQLVC.dbo.UserWorkspace WHERE 
                DatabaseName=@EventData.value('(/EVENT_INSTANCE/DatabaseName)[1]',  'NVARCHAR(255)') and 
                SchemaName=@EventData.value('(/EVENT_INSTANCE/SchemaName)[1]',  'NVARCHAR(255)') and 
                ObjectName=@EventData.value('(/EVENT_INSTANCE/ObjectName)[1]',  'NVARCHAR(255)') and 
                ObjectType=@EventData.value('(/EVENT_INSTANCE/ObjectType)[1]',  'NVARCHAR(255)') and 
                LoginName=SUSER_SNAME())
                begin
                    INSERT INTO SQLVC.dbo.UserWorkspace(DatabaseName, SchemaName, ObjectName, ObjectType, LoginName)
                    values(@EventData.value('(/EVENT_INSTANCE/DatabaseName)[1]',  'NVARCHAR(255)'),
                    @EventData.value('(/EVENT_INSTANCE/SchemaName)[1]',  'NVARCHAR(255)'),
                    @EventData.value('(/EVENT_INSTANCE/ObjectName)[1]',  'NVARCHAR(255)'),
                    @EventData.value('(/EVENT_INSTANCE/ObjectType)[1]',  'NVARCHAR(255)'), SUSER_NAME())
                end;
 
    INSERT SQLVC.dbo.DDLEvents
    (
        EventType,
        EventDDL,
        DatabaseName,
        SchemaName,
        ObjectName,
		ObjectType,
        HostName,
        IPAddress,
        ProgramName,
        LoginName,
        EventDate
    )
    SELECT
        @EventData.value('(/EVENT_INSTANCE/EventType)[1]',   'NVARCHAR(100)'), 
        @EventData.value('(/EVENT_INSTANCE/TSQLCommand)[1]', 'NVARCHAR(MAX)'),
        @EventData.value('(/EVENT_INSTANCE/DatabaseName)[1]',  'NVARCHAR(255)'),--DB_NAME(),
        @EventData.value('(/EVENT_INSTANCE/SchemaName)[1]',  'NVARCHAR(255)'), 
        @EventData.value('(/EVENT_INSTANCE/ObjectName)[1]',  'NVARCHAR(255)'),
        @EventData.value('(/EVENT_INSTANCE/ObjectType)[1]',  'NVARCHAR(255)'),
        HOST_NAME(),
        @ip,
        PROGRAM_NAME(),
        SUSER_SNAME(),
        GETDATE();
END




