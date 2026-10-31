CREATE PROCEDURE dbo.usp_load_gold @year_month varchar(7) = NULL AS
BEGIN
  DELETE FROM dbo.fact_trip WHERE @year_month IS NULL OR year_month = @year_month;

  INSERT INTO dbo.fact_trip
  SELECT t.trip_key, t.year_month,
         CONVERT(int, CONVERT(char(8), t.pickup_ts, 112)),
         t.pickup_location_id, t.dropoff_location_id, t.payment_type_id,
         CASE WHEN t.rate_code_id IN (1,2,3,4,5,6) THEN t.rate_code_id ELSE 99 END,
         CASE WHEN t.vendor_id IN (1,2,6) THEN t.vendor_id ELSE -1 END,
         t.trip_type_id, t.pickup_ts, t.passenger_count, t.trip_distance_mi, t.duration_min,
         t.fare_amount, t.extra, t.mta_tax, t.tip_amount, t.tolls_amount, t.improvement_surcharge,
         t.congestion_surcharge, t.cbd_congestion_fee, t.total_amount
  FROM lh_silver.dbo.trips AS t
  WHERE @year_month IS NULL OR t.year_month = @year_month;
END

GO