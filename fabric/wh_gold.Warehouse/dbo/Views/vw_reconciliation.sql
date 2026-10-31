CREATE VIEW dbo.vw_reconciliation AS
WITH load_a AS (
  SELECT year_month, file_rows, bronze_rows,
         ROW_NUMBER() OVER (PARTITION BY year_month ORDER BY loaded_at DESC) AS rn
  FROM lh_bronze.dbo.ops_load_audit),
silver_a AS (
  SELECT year_month, duplicates_removed, quarantine_rows, silver_rows,
         ROW_NUMBER() OVER (PARTITION BY year_month ORDER BY audited_at DESC) AS rn
  FROM lh_silver.dbo.ops_silver_audit),
silver_t AS (SELECT year_month, SUM(total_amount) AS silver_total FROM lh_silver.dbo.trips GROUP BY year_month),
gold_t AS (SELECT year_month, COUNT(*) AS gold_rows, SUM(total_amount) AS gold_total FROM dbo.fact_trip GROUP BY year_month)
SELECT l.year_month, l.file_rows, l.bronze_rows, s.duplicates_removed, s.quarantine_rows, s.silver_rows,
       g.gold_rows, st.silver_total, g.gold_total,
       CASE WHEN l.file_rows = l.bronze_rows THEN 'PASS' ELSE 'FAIL' END AS load_check,
       CASE WHEN l.bronze_rows = s.silver_rows + s.quarantine_rows + s.duplicates_removed THEN 'PASS' ELSE 'FAIL' END AS transform_check,
       CASE WHEN s.silver_rows = g.gold_rows AND st.silver_total = g.gold_total THEN 'PASS' ELSE 'FAIL' END AS publish_check
FROM load_a AS l
JOIN silver_a AS s ON s.year_month = l.year_month AND s.rn = 1
LEFT JOIN silver_t AS st ON st.year_month = l.year_month
LEFT JOIN gold_t AS g ON g.year_month = l.year_month
WHERE l.rn = 1;

GO