# Fabric notebook source

# METADATA ********************

# META {
# META   "kernel_info": {
# META     "name": "synapse_pyspark"
# META   },
# META   "dependencies": {
# META     "lakehouse": {
# META       "default_lakehouse": "1fedc5d1-0048-4ea3-a274-0c8b2d958e4a",
# META       "default_lakehouse_name": "lh_silver",
# META       "default_lakehouse_workspace_id": "13dbe4ca-0744-48cb-ad05-0f672bbd77fd",
# META       "known_lakehouses": [
# META         {
# META           "id": "1fedc5d1-0048-4ea3-a274-0c8b2d958e4a"
# META         }
# META       ]
# META     }
# META   }
# META }

# CELL ********************

%pip install "great_expectations>=1.0,<2" -q

# METADATA ********************

# META {
# META   "language": "python",
# META   "language_group": "synapse_pyspark"
# META }

# PARAMETERS CELL ********************

p_inject_bad_row = False
p_fail_on_error = True

# METADATA ********************

# META {
# META   "language": "python",
# META   "language_group": "synapse_pyspark"
# META }

# CELL ********************

import uuid
import great_expectations as gx
from pyspark.sql import functions as F

df = spark.table("trips")
if p_inject_bad_row:
    # Test only, in memory: duplicates one trip_key and gives it a negative total
    df = df.unionByName(df.limit(1).withColumn("total_amount", F.lit(-50).cast("decimal(10,2)")))

context = gx.get_context(mode="ephemeral")
batch_def = (context.data_sources.add_spark(name="silver")
             .add_dataframe_asset(name="trips")
             .add_batch_definition_whole_dataframe("all_rows"))
suite = context.suites.add(gx.ExpectationSuite(name="silver_trips_suite"))
for e in [
    gx.expectations.ExpectColumnValuesToBeUnique(column="trip_key"),
    gx.expectations.ExpectColumnValuesToNotBeNull(column="pickup_ts"),
    gx.expectations.ExpectColumnValuesToNotBeNull(column="pickup_location_id"),
    gx.expectations.ExpectColumnPairValuesAToBeGreaterThanB(
        column_A="dropoff_ts", column_B="pickup_ts", or_equal=True, ignore_row_if="either_value_is_missing"),
    gx.expectations.ExpectColumnValuesToBeBetween(column="total_amount", min_value=0, max_value=1000),
    gx.expectations.ExpectColumnValuesToBeInSet(column="payment_type_id", value_set=[0, 1, 2, 3, 4, 5, 6]),
]:
    suite.add_expectation(e)

results = batch_def.get_batch(batch_parameters={"dataframe": df}).validate(suite)
print("Suite passed:", results.success)

# METADATA ********************

# META {
# META   "language": "python",
# META   "language_group": "synapse_pyspark"
# META }

# CELL ********************

run_id = str(uuid.uuid4())
rows = []
for r in results.results:
    cfg = r.expectation_config
    etype = getattr(cfg, "type", None) or getattr(cfg, "expectation_type", "")
    col = cfg.kwargs.get("column") or f'{cfg.kwargs.get("column_A")} >= {cfg.kwargs.get("column_B")}'
    rows.append((run_id, etype, col, bool(r.success),
                 int(r.result.get("unexpected_count") or 0), int(r.result.get("element_count") or 0),
                 bool(p_inject_bad_row)))

out = (spark.createDataFrame(rows, "run_id string, expectation string, column_name string, success boolean, "
                                   "unexpected_count long, element_count long, injected_test boolean")
       .withColumn("checked_at", F.current_timestamp()))
out.write.format("delta").mode("append").saveAsTable("ops_dq_results")
display(out)

if p_fail_on_error and not results.success:
    failed = sum(1 for r in results.results if not r.success)
    raise Exception(f"Great Expectations suite failed: {failed} expectation(s) failed. Run {run_id}")

# METADATA ********************

# META {
# META   "language": "python",
# META   "language_group": "synapse_pyspark"
# META }
