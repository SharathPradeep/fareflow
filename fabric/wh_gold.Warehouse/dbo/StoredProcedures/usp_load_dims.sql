CREATE PROCEDURE dbo.usp_load_dims AS
BEGIN
  TRUNCATE TABLE dbo.dim_date;
  INSERT INTO dbo.dim_date
  SELECT date_key, [date], [year], [month], month_name, day_of_week, is_weekend FROM lh_silver.dbo.dim_date;

  TRUNCATE TABLE dbo.dim_zone;
  INSERT INTO dbo.dim_zone SELECT location_id, borough, zone, service_zone FROM lh_silver.dbo.zones;

  TRUNCATE TABLE dbo.dim_payment_type;
  INSERT INTO dbo.dim_payment_type
  SELECT 0, 'Flex Fare' UNION ALL SELECT 1, 'Credit card' UNION ALL SELECT 2, 'Cash' UNION ALL
  SELECT 3, 'No charge' UNION ALL SELECT 4, 'Dispute' UNION ALL SELECT 5, 'Unknown' UNION ALL SELECT 6, 'Voided trip';

  TRUNCATE TABLE dbo.dim_rate_code;
  INSERT INTO dbo.dim_rate_code
  SELECT 1, 'Standard rate' UNION ALL SELECT 2, 'JFK' UNION ALL SELECT 3, 'Newark' UNION ALL
  SELECT 4, 'Nassau or Westchester' UNION ALL SELECT 5, 'Negotiated fare' UNION ALL
  SELECT 6, 'Group ride' UNION ALL SELECT 99, 'Unknown';

  TRUNCATE TABLE dbo.dim_vendor;
  INSERT INTO dbo.dim_vendor
  SELECT -1, 'Unknown' UNION ALL SELECT 1, 'Creative Mobile Technologies' UNION ALL
  SELECT 2, 'Curb Mobility' UNION ALL SELECT 6, 'Myle Technologies';
END

GO