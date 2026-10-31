CREATE   PROCEDURE dbo.usp_snapshot_ops AS
BEGIN
  IF OBJECT_ID('dbo.recon_monthly') IS NOT NULL DROP TABLE dbo.recon_monthly;
  CREATE TABLE dbo.recon_monthly AS
  SELECT *, CAST(SYSDATETIME() AS datetime2(6)) AS checked_at FROM dbo.vw_reconciliation;

  IF OBJECT_ID('dbo.dq_quarantine_summary') IS NOT NULL DROP TABLE dbo.dq_quarantine_summary;
  CREATE TABLE dbo.dq_quarantine_summary AS
  SELECT year_month, dq_reason, COUNT(*) AS rows_quarantined
  FROM lh_silver.dbo.trips_quarantine GROUP BY year_month, dq_reason;

  IF OBJECT_ID('dbo.dq_gx_results') IS NOT NULL DROP TABLE dbo.dq_gx_results;
  CREATE TABLE dbo.dq_gx_results AS SELECT * FROM lh_silver.dbo.ops_dq_results;
END

GO