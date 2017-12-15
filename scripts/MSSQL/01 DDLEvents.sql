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
	[EventDate] [datetime] NULL
) ON [PRIMARY] TEXTIMAGE_ON [PRIMARY]


CREATE TABLE [dbo].[UserWorkspace](
	[EventType] [varchar](max) NOT NULL,
	[EventDDL] [varchar](max) NULL,
	[DatabaseName] [varchar](max) NULL,
	[SchemaName] [varchar](max) NULL,
	[ObjectName] [varchar](max) NULL,
	[HostName] [varchar](max) NULL,
	[IPAddress] [varchar](max) NULL,
	[ProgramName] [varchar](max) NULL,
	[LoginName] [varchar](max) NULL
) ON [PRIMARY] TEXTIMAGE_ON [PRIMARY]
