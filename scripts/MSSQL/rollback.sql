IF EXISTS (SELECT * FROM sys.server_triggers WHERE [name] = N'SQLGitEventLogger' AND [type] = 'TR')
BEGIN
      DROP TRIGGER [SQLGitEventLogger] ON ALL SERVER;
END;