-- Delete week old ticket prices automatically using a SQL Agent Job
USE msdb;
GO

EXEC dbo.sp_add_job
	@job_name = N'Weekly Ticket Deletion';
GO

EXEC dbo.sp_add_jobstep
	@job_name = N'Weekly Ticket Deletion',
	@step_name = N'Delete expedia tickets',
	@subsystem = N'TSQL',
	@command = N'DELETE FROM expedia WHERE GETDATE() > DATEADD(week, 1, date_scrape);',
	@database_name = N'AirFare';
GO

EXEC dbo.sp_add_schedule
	@schedule_name = N'Once Every Mon 6:30AM',
	@freq_type = 8,
	@freq_interval = 2,
	@freq_subday_type = 0x1,
	@freq_recurrence_factor = 1,
	@active_start_date = 20231002,
	@active_end_date = 20241007,
	@active_start_time = 093000;
GO

EXEC dbo.sp_attach_schedule
	@job_name = N'Weekly Ticket Deletion',
	@schedule_name = N'Once Every Mon 6:30AM';
GO

EXEC dbo.sp_add_jobserver
	@job_name = N'Weekly Ticket Deletion';
GO

-- Use this if we want to delete a job
/*
EXEC sp_delete_job
	@job_name = N'Weekly Ticket Deletion';
GO
*/
