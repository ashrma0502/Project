-- TABLE: silver_country_dim
INSERT IGNORE INTO silver_country_dim(iso2_code,iso3_code,country_name,region_name,income_group,is_active,load_timestamp)
VALUES(:iso2_code,:iso3_code,:country_name,:region_name,:income_group,:is_active,:load_timestamp)

-- TABLE: silver_indicator_dim
INSERT IGNORE INTO silver_indicator_dim(indicator_code,indicator_name,unit,source_system,load_timestamp)
VALUES (:indicator_code,:indicator_name,:unit,:source_system,:load_timestamp)

-- TABLE: silver_calendar_year
INSERT IGNORE INTO silver_calendar_year (year)
VALUES (:year)

-- TABLE: silver_indicator_fact
INSERT IGNORE INTO silver_indicator_fact(pipeline_run_id,indicator_code,country_iso2,country_iso3,year,indicator_value,unit,obs_status,decimals,ingestion_timestamp)
VALUES(:pipeline_run_id,:indicator_code,:country_iso2,:country_iso3,:year,:indicator_value,:unit,:obs_status,:decimals,:ingestion_timestamp)
