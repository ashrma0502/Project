-- Silver layer: country dim, indicator dim, calendar year, observation fact.

CREATE TABLE IF NOT EXISTS silver_country_dim(
    country_id     INT          NOT NULL AUTO_INCREMENT,
    iso2_code      VARCHAR(5)   NOT NULL,
    iso3_code      VARCHAR(5)   NOT NULL,
    country_name   VARCHAR(150) NOT NULL,
    region_name    VARCHAR(100) NULL,
    income_group   VARCHAR(100) NULL,
    is_active      TINYINT      NOT NULL DEFAULT 1,
    load_timestamp DATETIME     NULL,
    PRIMARY KEY (country_id),
    UNIQUE KEY uq_country_iso2 (iso2_code)
);

CREATE TABLE IF NOT EXISTS silver_indicator_dim(
    indicator_id   INT          NOT NULL AUTO_INCREMENT,
    indicator_code VARCHAR(50)  NOT NULL,
    indicator_name VARCHAR(255) NOT NULL,
    unit           VARCHAR(100) NULL,
    source_system  VARCHAR(100) NULL,
    load_timestamp DATETIME     NULL,
    PRIMARY KEY (indicator_id),
    UNIQUE KEY uq_indicator_code (indicator_code)
);

CREATE TABLE IF NOT EXISTS silver_calendar_year(
    year SMALLINT NOT NULL,
    PRIMARY KEY (year)
);

CREATE TABLE IF NOT EXISTS silver_indicator_fact(
    fact_id             INT          NOT NULL AUTO_INCREMENT,
    pipeline_run_id     VARCHAR(30)  NULL,
    indicator_code      VARCHAR(50)  NOT NULL,
    country_iso2        VARCHAR(5)   NOT NULL,
    country_iso3        VARCHAR(5)   NOT NULL,
    year                SMALLINT     NOT NULL,
    indicator_value     DOUBLE       NULL,
    unit                VARCHAR(100) NULL,
    obs_status          VARCHAR(50)  NULL,
    decimals            TINYINT      NULL,
    ingestion_timestamp DATETIME     NULL,
    PRIMARY KEY (fact_id),
    UNIQUE KEY uq_fact_key (country_iso3,indicator_code,year),
    INDEX idx_year           (year),
    INDEX idx_country_iso3   (country_iso3),
    INDEX idx_indicator_code (indicator_code)
);