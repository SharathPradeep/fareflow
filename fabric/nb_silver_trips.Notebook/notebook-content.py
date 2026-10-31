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
# META         },
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

from pyspark.sql import Window
from pyspark.sql import functions as F
from pyspark.sql.types import IntegerType, StringType, StructField, StructType


bronze_zones = spark.table("lh_bronze.taxi_zone_lookup")
zone_ids = bronze_zones.select(F.col("LocationID").alias("location_id")).distinct()

zones = (
    bronze_zones.select(
        F.col("LocationID").cast("int").alias("location_id"),
        F.col("Borough").alias("borough"),
        F.col("Zone").alias("zone"),
        F.col("service_zone").alias("service_zone"),
    )
    .filter(F.col("location_id").isNull() | (F.col("location_id") != -1))
)
unknown_zone = spark.createDataFrame(
    [(-1, "Unknown", "Unknown", "Unknown")],
    schema=StructType(
        [
            StructField("location_id", IntegerType(), False),
            StructField("borough", StringType(), False),
            StructField("zone", StringType(), False),
            StructField("service_zone", StringType(), False),
        ]
    ),
)
zones.unionByName(unknown_zone).write.format("delta").mode("overwrite").saveAsTable(
    "zones"
)


def write_month_partition(dataframe, table_name, month):
    writer = dataframe.write.format("delta").partitionBy("year_month")
    if spark.catalog.tableExists(table_name):
        (
            writer.mode("overwrite")
            .option("replaceWhere", f"year_month = '{month}'")
            .saveAsTable(table_name)
        )
    else:
        writer.mode("overwrite").saveAsTable(table_name)


for month in p_months.split(","):
    bronze_month = spark.table("lh_bronze.green_trips").filter(
        F.col("year_month") == month
    )
    bronze_rows = bronze_month.count()
    trips = bronze_month.select(
        F.col("VendorID").alias("vendor_id"),
        F.col("lpep_pickup_datetime").alias("pickup_ts"),
        F.col("lpep_dropoff_datetime").alias("dropoff_ts"),
        F.col("PULocationID").alias("pickup_location_id"),
        F.col("DOLocationID").alias("dropoff_location_id"),
        F.coalesce(F.col("RatecodeID"), F.lit(99)).alias("rate_code_id"),
        F.coalesce(F.col("payment_type"), F.lit(5)).alias("payment_type_id"),
        F.col("trip_type").alias("trip_type_id"),
        F.col("passenger_count").alias("passenger_count"),
        F.col("trip_distance").alias("trip_distance_mi"),
        F.col("fare_amount").cast("decimal(10,2)").alias("fare_amount"),
        F.col("extra").cast("decimal(10,2)").alias("extra"),
        F.col("mta_tax").cast("decimal(10,2)").alias("mta_tax"),
        F.col("tip_amount").cast("decimal(10,2)").alias("tip_amount"),
        F.col("tolls_amount").cast("decimal(10,2)").alias("tolls_amount"),
        F.col("improvement_surcharge")
        .cast("decimal(10,2)")
        .alias("improvement_surcharge"),
        F.col("congestion_surcharge")
        .cast("decimal(10,2)")
        .alias("congestion_surcharge"),
        F.coalesce(
            F.col("cbd_congestion_fee").cast("decimal(10,2)"),
            F.lit(0).cast("decimal(10,2)"),
        ).alias("cbd_congestion_fee"),
        F.col("total_amount").cast("decimal(10,2)").alias("total_amount"),
        F.col("year_month"),
        F.col("_ingested_at"),
    ).withColumn(
        "duration_min",
        (
            F.unix_timestamp("dropoff_ts") - F.unix_timestamp("pickup_ts")
        )
        / 60.0,
    )

    trip_key_columns = [
        "vendor_id",
        "pickup_ts",
        "dropoff_ts",
        "pickup_location_id",
        "dropoff_location_id",
        "trip_distance_mi",
        "total_amount",
    ]
    trips = trips.withColumn(
        "trip_key",
        F.sha2(
            F.concat_ws(
                "|",
                *[
                    F.coalesce(F.col(column).cast("string"), F.lit(""))
                    for column in trip_key_columns
                ],
            ),
            256,
        ),
    )

    dedup_window = Window.partitionBy("trip_key").orderBy(
        F.col("_ingested_at").desc_nulls_last()
    )
    ranked_trips = trips.withColumn(
        "_duplicate_rank", F.row_number().over(dedup_window)
    )
    duplicates_removed = ranked_trips.filter(
        F.col("_duplicate_rank") > 1
    ).count()
    trips = ranked_trips.filter(F.col("_duplicate_rank") == 1).drop(
        "_duplicate_rank", "_ingested_at"
    )

    month_start = F.to_timestamp(F.lit(f"{month}-01"))
    next_month_start = F.add_months(month_start, 1)
    trips = trips.withColumn(
        "dq_reason",
        F.when(F.col("pickup_ts").isNull(), F.lit("pickup_ts is null"))
        .when(
            F.col("dropoff_ts") < F.col("pickup_ts"),
            F.lit("dropoff_ts before pickup_ts"),
        )
        .when(
            (F.col("pickup_ts") < month_start - F.expr("INTERVAL 1 DAY"))
            | (
                F.col("pickup_ts")
                >= next_month_start + F.expr("INTERVAL 1 DAY")
            ),
            F.lit("pickup_ts outside file month"),
        )
        .when(
            ~F.col("payment_type_id").between(0, 6),
            F.lit("payment_type_id outside 0-6"),
        )
        .when(
            F.col("trip_distance_mi") < 0,
            F.lit("trip_distance_mi is negative"),
        )
        .when(
            (F.col("total_amount") < 0) | (F.col("total_amount") > 1000),
            F.lit("total_amount outside 0-1000"),
        ),
    )

    trips = (
        trips.join(
            F.broadcast(
                zone_ids.select(
                    F.col("location_id").alias("_pickup_zone_id")
                )
            ),
            trips.pickup_location_id == F.col("_pickup_zone_id"),
            "left",
        )
        .withColumn(
            "pickup_location_id",
            F.coalesce(F.col("_pickup_zone_id"), F.lit(-1)),
        )
        .drop("_pickup_zone_id")
        .join(
            F.broadcast(
                zone_ids.select(
                    F.col("location_id").alias("_dropoff_zone_id")
                )
            ),
            F.col("dropoff_location_id") == F.col("_dropoff_zone_id"),
            "left",
        )
        .withColumn(
            "dropoff_location_id",
            F.coalesce(F.col("_dropoff_zone_id"), F.lit(-1)),
        )
        .drop("_dropoff_zone_id")
    )

    silver_trips = trips.filter(F.col("dq_reason").isNull()).drop("dq_reason")
    quarantine_trips = trips.filter(F.col("dq_reason").isNotNull())
    silver_rows = silver_trips.count()
    quarantine_rows = quarantine_trips.count()

    write_month_partition(silver_trips, "trips", month)
    write_month_partition(quarantine_trips, "trips_quarantine", month)

    status = (
        "OK"
        if bronze_rows
        == silver_rows + quarantine_rows + duplicates_removed
        else "MISMATCH"
    )
    (
        spark.createDataFrame(
            [
                (
                    month,
                    bronze_rows,
                    duplicates_removed,
                    quarantine_rows,
                    silver_rows,
                    status,
                )
            ],
            [
                "year_month",
                "bronze_rows",
                "duplicates_removed",
                "quarantine_rows",
                "silver_rows",
                "status",
            ],
        )
        .withColumn("audited_at", F.current_timestamp())
        .select(
            "year_month",
            "bronze_rows",
            "duplicates_removed",
            "quarantine_rows",
            "silver_rows",
            "status",
            "audited_at",
        )
        .write.format("delta")
        .mode("append")
        .saveAsTable("ops_silver_audit")
    )

# METADATA ********************

# META {
# META   "language": "python",
# META   "language_group": "synapse_pyspark"
# META }

# CELL ********************

date_range = spark.range(0, 731).select(
    F.date_add(F.to_date(F.lit("2024-01-01")), F.col("id").cast("int")).alias(
        "date"
    )
)
dim_date = date_range.select(
    F.date_format("date", "yyyyMMdd").cast("int").alias("date_key"),
    "date",
    F.year("date").alias("year"),
    F.month("date").alias("month"),
    F.date_format("date", "MMMM").alias("month_name"),
    F.date_format("date", "EEEE").alias("day_of_week"),
    F.dayofweek("date").isin(1, 7).alias("is_weekend"),
)
dim_date.write.format("delta").mode("overwrite").saveAsTable("dim_date")

# METADATA ********************

# META {
# META   "language": "python",
# META   "language_group": "synapse_pyspark"
# META }

# CELL ********************

display(spark.sql("SELECT * FROM ops_silver_audit ORDER BY audited_at DESC, year_month LIMIT 6"))
display(spark.sql("SELECT dq_reason, COUNT(*) AS rows FROM trips_quarantine GROUP BY dq_reason ORDER BY rows DESC"))

# METADATA ********************

# META {
# META   "language": "python",
# META   "language_group": "synapse_pyspark"
# META }
