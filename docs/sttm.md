# Source-to-target mapping

Source: NYC TLC green taxi trip records (monthly parquet) and the taxi zone lookup (CSV).
Reference: TLC green trip data dictionary.

## Bronze: `lh_bronze.green_trips`

Source columns are kept with their original names. Known columns are cast to declared types. New columns pass through via `mergeSchema`.

| Added column | Rule |
|---|---|
| `year_month` | Taken from the file name, not the pickup date. Partition column |
| `_source_file` | Path of the landed file |
| `_ingested_at` | Load timestamp |
| `_run_id` | Notebook run identifier |

## Silver and gold

| Source (green parquet) | Silver (`lh_silver.trips`) | Rule | Gold (`wh_gold.fact_trip`) |
|---|---|---|---|
| VendorID | vendor_id | Cast to int | vendor_key (codes 1, 2, 6 else -1) |
| lpep_pickup_datetime | pickup_ts | Must be within the file month plus or minus one day, else quarantine | date_key (yyyymmdd), pickup_ts |
| lpep_dropoff_datetime | dropoff_ts | Must not be before pickup_ts, else quarantine | used for duration_min |
| PULocationID | pickup_location_id | Not in zone lookup becomes -1 (unknown) | pickup_zone_key (role-playing dim_zone) |
| DOLocationID | dropoff_location_id | Same as pickup | dropoff_zone_key (inactive relationship) |
| RatecodeID | rate_code_id | Null becomes 99 (unknown) | rate_code_key (codes 1 to 6 else 99) |
| payment_type | payment_type_id | Null becomes 5 (unknown). Outside 0 to 6 is quarantined | payment_type_key |
| trip_type | trip_type_id | As is | trip_type_id |
| passenger_count | passenger_count | As is | passenger_count |
| trip_distance | trip_distance_mi | Negative is quarantined | trip_distance_mi |
| fare_amount, extra, mta_tax, tip_amount, tolls_amount, improvement_surcharge, congestion_surcharge | same names | decimal(10,2) | same names |
| cbd_congestion_fee | cbd_congestion_fee | Absent before 2025: null in bronze, 0 in silver | cbd_congestion_fee |
| total_amount | total_amount | decimal(10,2). Below 0 or above 1,000 is quarantined | total_amount |
| (derived) | duration_min | Minutes from pickup to dropoff | duration_min |
| (derived) | trip_key | SHA-256 of vendor, pickup, dropoff, zones, distance and total. Duplicates keep the latest ingestion | trip_key (degenerate dimension) |
| (derived) | year_month | From bronze | year_month |
| taxi_zone_lookup.csv | lh_silver.zones | Renamed columns plus unknown member -1 | dim_zone |
| (generated) | lh_silver.dim_date | 2024-01-01 to 2025-12-31 | dim_date |
| TLC data dictionary | (reference) | Code lists | dim_payment_type, dim_rate_code, dim_vendor |

## Quarantine reasons (`lh_silver.trips_quarantine.dq_reason`)

First failing rule wins: pickup missing, dropoff before pickup, pickup outside file month, invalid payment type, negative distance, total out of range.
