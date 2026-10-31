CREATE TABLE [dbo].[dim_date] (
    [date_key]    INT          NOT NULL,
    [date]        DATE         NOT NULL,
    [year]        INT          NULL,
    [month]       INT          NULL,
    [month_name]  VARCHAR (20) NULL,
    [day_of_week] VARCHAR (20) NULL,
    [is_weekend]  BIT          NULL
);


GO