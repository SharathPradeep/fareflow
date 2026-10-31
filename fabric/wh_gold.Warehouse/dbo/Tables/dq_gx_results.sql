CREATE TABLE [dbo].[dq_gx_results] (
    [run_id]           VARCHAR (8000) NULL,
    [expectation]      VARCHAR (8000) NULL,
    [column_name]      VARCHAR (8000) NULL,
    [success]          BIT            NULL,
    [unexpected_count] BIGINT         NULL,
    [element_count]    BIGINT         NULL,
    [injected_test]    BIT            NULL,
    [checked_at]       DATETIME2 (6)  NULL
);


GO