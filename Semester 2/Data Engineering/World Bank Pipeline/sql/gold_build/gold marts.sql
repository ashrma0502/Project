TRUNCATE TABLE gold_country_indicator_year;
INSERT INTO gold_country_indicator_year(country_iso3,country_name,region_name,indicator_code,indicator_name,year,indicator_value,unit,obs_status,pipeline_run_id)
SELECT f.country_iso3,c.country_name,c.region_name,f.indicator_code,d.indicator_name,f.year,f.indicator_value,f.unit,f.obs_status,f.pipeline_run_id
FROM silver_indicator_fact f
LEFT JOIN silver_country_dim   c ON c.iso3_code=f.country_iso3
LEFT JOIN silver_indicator_dim d ON d.indicator_code=f.indicator_code;

TRUNCATE TABLE gold_region_indicator_summary;
INSERT INTO gold_region_indicator_summary(region_name,year,indicator_code,indicator_name,avg_value,min_value,max_value,country_count)
SELECT c.region_name,f.year,f.indicator_code,d.indicator_name,
       ROUND(AVG(f.indicator_value),4),ROUND(MIN(f.indicator_value),4),
       ROUND(MAX(f.indicator_value),4),COUNT(DISTINCT f.country_iso3)
FROM silver_indicator_fact f
JOIN silver_country_dim    c ON c.iso3_code=f.country_iso3
JOIN silver_indicator_dim  d ON d.indicator_code=f.indicator_code
WHERE f.indicator_value IS NOT NULL AND c.region_name IS NOT NULL AND c.region_name<>''
GROUP BY c.region_name,f.year,f.indicator_code,d.indicator_name;

TRUNCATE TABLE gold_country_vs_region;
INSERT INTO gold_country_vs_region(country_iso3,country_name,region_name,year,indicator_code,country_value,region_avg_value,variance_from_region)
SELECT f.country_iso3,c.country_name,c.region_name,f.year,f.indicator_code,
       f.indicator_value,r.avg_value,ROUND(f.indicator_value-r.avg_value,4)
FROM silver_indicator_fact          f
JOIN silver_country_dim             c ON c.iso3_code=f.country_iso3
JOIN gold_region_indicator_summary  r ON r.region_name=c.region_name AND r.year=f.year AND r.indicator_code=f.indicator_code
WHERE f.indicator_value IS NOT NULL;

TRUNCATE TABLE gold_top_countries_by_indicator;
INSERT INTO gold_top_countries_by_indicator(year,indicator_code,indicator_name,country_iso3,country_name,indicator_value,country_rank)
SELECT f.year,f.indicator_code,d.indicator_name,f.country_iso3,c.country_name,f.indicator_value,
       RANK() OVER (PARTITION BY f.year,f.indicator_code ORDER BY f.indicator_value DESC)
FROM silver_indicator_fact f
JOIN silver_country_dim    c ON c.iso3_code=f.country_iso3
JOIN silver_indicator_dim  d ON d.indicator_code=f.indicator_code
WHERE f.indicator_value IS NOT NULL;

TRUNCATE TABLE gold_indicator_yoy_change;
INSERT INTO gold_indicator_yoy_change(country_iso3,country_name,indicator_code,indicator_name,year,current_value,previous_value,absolute_change,percent_change)
SELECT f.country_iso3,c.country_name,f.indicator_code,d.indicator_name,f.year,f.indicator_value,
    LAG(f.indicator_value) OVER (PARTITION BY f.country_iso3,f.indicator_code ORDER BY f.year),
    ROUND(f.indicator_value-LAG(f.indicator_value) OVER (PARTITION BY f.country_iso3,f.indicator_code ORDER BY f.year),4),
    ROUND(100.0*(f.indicator_value-LAG(f.indicator_value) OVER (PARTITION BY f.country_iso3,f.indicator_code ORDER BY f.year))
    / NULLIF(LAG(f.indicator_value) OVER (PARTITION BY f.country_iso3,f.indicator_code ORDER BY f.year),0),4)
FROM silver_indicator_fact f
JOIN silver_country_dim    c ON c.iso3_code=f.country_iso3
JOIN silver_indicator_dim  d ON d.indicator_code=f.indicator_code
WHERE f.indicator_value IS NOT NULL;

TRUNCATE TABLE gold_data_completeness_report;
INSERT INTO gold_data_completeness_report(indicator_code,indicator_name,country_count,missing_value_count,total_rows,completeness_pct,last_refresh_timestamp)
SELECT f.indicator_code,d.indicator_name,COUNT(DISTINCT f.country_iso3),
       SUM(CASE WHEN f.indicator_value IS NULL THEN 1 ELSE 0 END),COUNT(*),
       ROUND(100.0*SUM(CASE WHEN f.indicator_value IS NOT NULL THEN 1 ELSE 0 END)/COUNT(*),2),NOW()
FROM silver_indicator_fact f
JOIN silver_indicator_dim  d ON d.indicator_code=f.indicator_code
GROUP BY f.indicator_code,d.indicator_name;
