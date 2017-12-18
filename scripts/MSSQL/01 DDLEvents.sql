--create DDLEventsTable
USE [SQLVC]


CREATE TABLE [dbo].[DDLEvents](
	[RowID] [int] IDENTITY(1,1) NOT NULL,
	[EventType] [varchar](max) NOT NULL,
	[EventDDL] [varchar](max) NULL,
	[DatabaseName] [varchar](max) NULL,
	[SchemaName] [varchar](max) NULL,
	[ObjectName] [varchar](max) NULL,
	[ObjectType] [varchar](max) NULL,
	[HostName] [varchar](max) NULL,
	[IPAddress] [varchar](max) NULL,
	[ProgramName] [varchar](max) NULL,
	[LoginName] [varchar](max) NULL,
	[EventDate] [datetime] DEFAULT GETDATE()
) ON [PRIMARY] TEXTIMAGE_ON [PRIMARY]


CREATE TABLE [dbo].[UserWorkspace](
	[RowID] [int] IDENTITY(1,1) NOT NULL,
	[DatabaseName] [varchar](max) NULL,
	[SchemaName] [varchar](max) NULL,
	[ObjectName] [varchar](max) NULL,
	[LoginName] [varchar](max) NULL,
	[ObjectType] [varchar](max) NULL
) ON [PRIMARY] TEXTIMAGE_ON [PRIMARY]

CREATE TABLE [dbo].[Commits_hdr](
	[RowID] [int] IDENTITY(1,1) NOT NULL,
	[CommitID] [varchar](max) NULL,
	[LoginName] [varchar](max) NULL,
	[ChangesetDate] [datetime] default GETDATE(),
	[CommitMessage] [varchar](max) NULL,
) ON [PRIMARY] TEXTIMAGE_ON [PRIMARY]

CREATE TABLE [dbo].[Commits_dtl](
	[RowID] [int] IDENTITY(1,1) NOT NULL,
	[CommitID] [varchar](max) NULL,
	[DatabaseName] [varchar](max) NULL,
	[SchemaName] [varchar](max) NULL,
	[ObjectName] [varchar](max) NULL,
	[LoginName] [varchar](max) NULL,
	[ObjectType] [varchar](max) NULL,
	[ObjectDDL] [varchar](max) NULL
) ON [PRIMARY] TEXTIMAGE_ON [PRIMARY]