CREATE TABLE [dbo].[ops_pipeline_runs] (
    [run_id]        VARCHAR (64)  NULL,
    [pipeline_name] VARCHAR (100) NULL,
    [status]        VARCHAR (20)  NULL,
    [logged_at]     DATETIME2 (6) NULL
);


GO