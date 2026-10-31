CREATE TABLE [dbo].[dq_quarantine_summary] (
    [year_month]       VARCHAR (2048) NULL,
    [dq_reason]        VARCHAR (8000) NULL,
    [rows_quarantined] INT            NULL
);


GO