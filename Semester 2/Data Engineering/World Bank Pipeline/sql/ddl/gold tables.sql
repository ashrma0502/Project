CREATE TABLE IF NOT EXISTS gold_country_indicator_year(
    country_iso3    VARCHAR(5)   NOT NULL,
    country_name    VARCHAR(150) NOT NULL,
    region_name     VARCHAR(100) NULL,
    indicator_code  VARCHAR(50)  NOT NULL,
    indicator_name  VARCHAR(255) NULL,
    year            SMALLINT     NOT NULL,
    indicator_value DOUBLE       NULL,
    unit            VARCHAR(100) NULL,
    obs_status      VARCHAR(50)  NULL,
    pipeline_run_id VARCHAR(30)  NULL,
    PRIMARY KEY (country_iso3,indicator_code,year)
);

CREATE TABLE IF NOT EXISTS gold_region_indicator_summary(
    region_name     VARCHAR(100) NULL,
    year            SMALLINT     NOT NULL,
    indicator_code  VARCHAR(50)  NOT NULL,
    indicator_name  VARCHAR(255) NULL,
    avg_value       DOUBLE       NULL,
    min_value       DOUBLE       NULL,
    max_value       DOUBLE       NULL,
    country_count   INT          NULL,
    PRIMARY KEY (region_name,indicator_code,year)
);

CREATE TABLE IF NOT EXISTS gold_country_vs_region(
    country_iso3         VARCHAR(5)   NOT NULL,
    country_name         VARCHAR(150) NULL,
    region_name          VARCHAR(100) NULL,
    year                 SMALLINT     NOT NULL,
    indicator_code       VARCHAR(50)  NOT NULL,
    country_value        DOUBLE       NULL,
    region_avg_value     DOUBLE       NULL,
    variance_from_region DOUBLE       NULL,
    PRIMARY KEY (country_iso3,indicator_code, year)
);

CREATE TABLE IF NOT EXISTS gold_top_countries_by_indicator(
    year             SMALLINT      NOT NULL,
    indicator_code   VARCHAR(50)   NOT NULL,
    indicator_name   VARCHAR(255)  NULL,
    country_iso3     VARCHAR(5)    NOT NULL,
    country_name     VARCHAR(150)  NULL,
    indicator_value  DOUBLE        NULL,
    country_rank     INT           NULL,
    PRIMARY KEY (year,indicator_code,country_iso3)
);

CREATE TABLE IF NOT EXISTS gold_indicator_yoy_change(
    country_iso3    VARCHAR(5)   NOT NULL,
    country_name    VARCHAR(150) NULL,
    indicator_code  VARCHAR(50)  NOT NULL,
    indicator_name  VARCHAR(255) NULL,
    year            SMALLINT     NOT NULL,
    current_value   DOUBLE       NULL,
    previous_value  DOUBLE       NULL,
    absolute_change DOUBLE       NULL,
    percent_change  DOUBLE       NULL,
    PRIMARY KEY (country_iso3,indicator_code,year)
);

CREATE TABLE IF NOT EXISTS gold_data_completeness_report(
    indicator_code         VARCHAR(50)  NOT NULL,
    indicator_name         VARCHAR(255) NULL,
    country_count          INT          NULL,
    missing_value_count    INT          NULL,
    total_rows             INT          NULL,
    completeness_pct       DOUBLE       NULL,
    last_refresh_timestamp DATETIME     NULL,
    PRIMARY KEY (indicator_code)
);