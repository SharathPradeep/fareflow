# Fabric notebook source

# METADATA ********************

# META {
# META   "kernel_info": {
# META     "name": "synapse_pyspark"
# META   },
# META   "dependencies": {
# META     "lakehouse": {
# META       "default_lakehouse": "a9d1674a-535f-43f8-95c1-07997cf7b5b9",
# META       "default_lakehouse_name": "lh_bronze",
# META       "default_lakehouse_workspace_id": "13dbe4ca-0744-48cb-ad05-0f672bbd77fd",
# META       "known_lakehouses": [
# META         {
# META           "id": "a9d1674a-535f-43f8-95c1-07997cf7b5b9"
# META         }
# META       ]
# META     }
# META   }
# META }

# PARAMETERS CELL ********************

p_months = "2024-10,2024-11,2024-12,2025-01,2025-02,2025-03"

# METADATA ********************

# META {
# META   "language": "python",
# META   "language_group": "synapse_pyspark"
# META }

# CELL ********************

import uuid
from pyspark.sql import functions as F

LANDING = "Files/landing/green"
TABLE = "green_trips"
RUN_ID = str(uuid.uuid4())

# Declared types for known columns. New columns pass through untouched.
TYPE_MAP = {
    "VendorID": "int", "lpep_pickup_datetime": "timestamp", "lpep_dropoff_datetime": "timestamp",
    "store_and_fwd_flag": "string", "RatecodeID": "int", "PULocationID": "int", "DOLocationID": "int",
    "passenger_count": "int", "trip_distance": "double", "fare_amount": "double", "extra": "double",
    "mta_tax": "double", "tip_amount": "double", "tolls_amount": "double", "ehail_fee": "double",
    "improvement_surcharge": "double", "total_amount": "double", "payment_type": "int",
    "trip_type": "int", "congestion_surcharge": "double", "cbd_congestion_fee": "double",
}

def load_month(m):
    src = f"{LANDING}/green_tripdata_{m}.parquet"
    df = spark.read.parquet(src)
    df = df.select([F.col(c).cast(TYPE_MAP[c]).alias(c) if c in TYPE_MAP else F.col(c) for c in df.columns])
    df = (df.withColumn("year_month", F.lit(m))
            .withColumn("_source_file", F.lit(src))
            .withColumn("_ingested_at", F.current_timestamp())
            .withColumn("_run_id", F.lit(RUN_ID)))
    file_rows = df.count()

    writer = df.write.format("delta").option("mergeSchema", "true").partitionBy("year_month")
    if spark.catalog.tableExists(TABLE):
        writer = writer.mode("overwrite").option("replaceWhere", f"year_month = '{m}'")
    else:
        writer = writer.mode("overwrite")
    writer.saveAsTable(TABLE)

    bronze_rows = spark.table(TABLE).where(F.col("year_month") == m).count()
    return (RUN_ID, m, src, file_rows, bronze_rows, "OK" if file_rows == bronze_rows else "MISMATCH")

results = [load_month(m.strip()) for m in p_months.split(",")]

audit = (spark.createDataFrame(results,
            "run_id string, year_month string, source_file string, file_rows long, bronze_rows long, status string")
         .withColumn("loaded_at", F.current_timestamp()))
audit.write.format("delta").mode("append").saveAsTable("ops_load_audit")
display(audit)

# METADATA ********************

# META {
# META   "language": "python",
# META   "language_group": "synapse_pyspark"
# META }

# CELL ********************

zones = (spark.read.option("header", True).option("inferSchema", True)
         .csv("Files/landing/reference/taxi_zone_lookup.csv"))
zones.write.format("delta").mode("overwrite").option("overwriteSchema", "true").saveAsTable("taxi_zone_lookup")
display(zones.limit(5))

# METADATA ********************

# META {
# META   "language": "python",
# META   "language_group": "synapse_pyspark"
# META }

# CELL ********************

# MAGIC %%sql
# MAGIC SELECT year_month, COUNT(*) AS trips, COUNT(cbd_congestion_fee) AS rows_with_cbd_fee
# MAGIC FROM green_trips GROUP BY year_month ORDER BY year_month

# METADATA ********************

# META {
# META   "language": "sparksql",
# META   "language_group": "synapse_pyspark"
# META }
