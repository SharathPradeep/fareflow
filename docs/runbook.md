# FareFlow runbook

## Where to look first

1. `wh_gold.dbo.ops_pipeline_runs` for the latest run status.
2. `pl_master` run history in the workspace Monitor hub to see which activity failed.
3. Report page 2 (Data quality and reconciliation) for row and money checks.

## Re-run or backfill a month

1. Open `pl_master` and click Run.
2. Set `p_months` to the month or months to reload, for example `2025-02` or `2025-02,2025-03`.
3. Each month is replaced, not appended, so a re-run never duplicates data.
4. Confirm page 2 shows "All months reconcile" for that month.

## Reconciliation shows FAIL

| Check | Meaning | Action |
|---|---|---|
| load_check | Rows in the file do not match rows in bronze | Re-run the month. If it repeats, inspect the landed file in `lh_bronze/Files/landing/green` |
| transform_check | Bronze does not equal silver + quarantine + duplicates | Re-run `nb_silver_trips` for the month and check `ops_silver_audit` |
| publish_check | Silver and gold differ in rows or money | Run `EXEC dbo.usp_load_gold '<yyyy-mm>'; EXEC dbo.usp_snapshot_ops;` in `wh_gold` |

## Great Expectations failed

1. Query `lh_silver.ops_dq_results` for the latest `run_id` and find rows where `success = false`.
2. `unexpected_count` shows how many rows broke the expectation.
3. Decide with the data owner whether to add a quarantine rule in silver or to accept and adjust the expectation.
4. Fix, merge through a pull request and re-run `pl_master` for the affected months.

## A new column appears in the source

1. Bronze absorbs it automatically (`mergeSchema`). Earlier months show null.
2. Agree the meaning and type with the client, then add it to the declared type map in `nb_bronze_load`.
3. Add it to `nb_silver_trips`, `fact_trip`, `usp_load_gold`, the semantic model and the mapping document.
4. Release through a pull request and the deployment pipeline.

## Gold step fails with "Invalid object name lh_silver.dbo..."

The lakehouse SQL endpoint has not caught up with the latest Spark write. Open the `lh_silver` SQL analytics endpoint, click Refresh and re-run the gold step.

## Release from DEV to TEST (deployment pipeline dp_fareflow)

Deploy in this order. Each stage depends on the one before it.

1. **Storage and code:** lh_bronze, lh_silver, the three notebooks and pl_ingest_green. Notebook default lakehouses auto-bind to the TEST lakehouses. Verify in each notebook's Explorer.
2. **Data:** in TEST run pl_ingest_green, nb_bronze_load, nb_silver_trips and nb_dq_gx. Refresh both lakehouse SQL endpoints.
3. **Warehouse:** deploy wh_gold, then run `EXEC dbo.usp_load_dims; EXEC dbo.usp_load_gold; EXEC dbo.usp_snapshot_ops;` and confirm vw_reconciliation shows PASS.
4. **Model, report and orchestration:** deploy sm_mobility, rpt_mobility and pl_master.
5. **Post-deployment step:** the Direct Lake model keeps DEV's OneLake path. In TEST open sm_mobility > TMDL view, drag in the `DirectLake - wh_gold` expression, replace the workspace and warehouse IDs in the URL with TEST's, Apply and refresh. Every redeploy of sm_mobility resets this.
6. **Post-deployment step:** in TEST's pl_master, reselect TEST's wh_gold on run_gold, log_success and log_failure. Deployment keeps DEV's SQL endpoint hostname on these Script activities.
7. **Smoke test:** check pl_master activities reference TEST items, run it with `p_months = 2025-03` and confirm a SUCCEEDED row in ops_pipeline_runs.

## Report shows errors for a viewer

The semantic model uses a fixed identity connection. Check `sm_mobility` > Settings > Gateway and cloud connections and confirm the connection is valid and single sign-on is off.
