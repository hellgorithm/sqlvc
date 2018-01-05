IF EXISTS (SELECT * FROM sys.server_triggers WHERE [name] = N'SQLGitEventLogger' AND [type] = 'TR')
BEGIN
	select 1
      --DROP TRIGGER [SQLGitEventLogger] ON ALL SERVER;
END;