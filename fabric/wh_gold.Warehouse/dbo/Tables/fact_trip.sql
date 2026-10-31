CREATE TABLE [dbo].[fact_trip] (
    [trip_key]              VARCHAR (64)    NOT NULL,
    [year_month]            VARCHAR (7)     NOT NULL,
    [date_key]              INT             NOT NULL,
    [pickup_zone_key]       INT             NOT NULL,
    [dropoff_zone_key]      INT             NOT NULL,
    [payment_type_key]      INT             NOT NULL,
    [rate_code_key]         INT             NOT NULL,
    [vendor_key]            INT             NOT NULL,
    [trip_type_id]          INT             NULL,
    [pickup_ts]             DATETIME2 (6)   NULL,
    [passenger_count]       INT             NULL,
    [trip_distance_mi]      FLOAT (53)      NULL,
    [duration_min]          FLOAT (53)      NULL,
    [fare_amount]           DECIMAL (10, 2) NULL,
    [extra]                 DECIMAL (10, 2) NULL,
    [mta_tax]               DECIMAL (10, 2) NULL,
    [tip_amount]            DECIMAL (10, 2) NULL,
    [tolls_amount]          DECIMAL (10, 2) NULL,
    [improvement_surcharge] DECIMAL (10, 2) NULL,
    [congestion_surcharge]  DECIMAL (10, 2) NULL,
    [cbd_congestion_fee]    DECIMAL (10, 2) NULL,
    [total_amount]          DECIMAL (10, 2) NULL
);


GO