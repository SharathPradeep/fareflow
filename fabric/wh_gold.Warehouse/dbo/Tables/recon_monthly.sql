CREATE TABLE [dbo].[recon_monthly] (
    [year_month]         VARCHAR (8000)  NULL,
    [file_rows]          BIGINT          NULL,
    [bronze_rows]        BIGINT          NULL,
    [duplicates_removed] BIGINT          NULL,
    [quarantine_rows]    BIGINT          NULL,
    [silver_rows]        BIGINT          NULL,
    [gold_rows]          INT             NULL,
    [silver_total]       DECIMAL (38, 2) NULL,
    [gold_total]         DECIMAL (38, 2) NULL,
    [load_check]         VARCHAR (4)     NOT NULL,
    [transform_check]    VARCHAR (4)     NOT NULL,
    [publish_check]      VARCHAR (4)     NOT NULL,
    [checked_at]         DATETIME2 (6)   NULL
);


GO