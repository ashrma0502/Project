-- Bronze layer: tracks every API request, batch file, and load status.
CREATE TABLE IF NOT EXISTS bronze_ingestion_log(
    log_id             INT           NOT NULL AUTO_INCREMENT,
    batch_id           VARCHAR(10)   NOT NULL,
    pipeline_run_id    VARCHAR(30)   NOT NULL,
    load_timestamp     DATETIME      NOT NULL,
    country            VARCHAR(100)  NOT NULL,
    indicator_name     VARCHAR(100)  NOT NULL,
    indicator_code     VARCHAR(50)   NULL,
    date_from          SMALLINT      NOT NULL,
    date_to            SMALLINT      NOT NULL,
    api_url            TEXT          NULL,
    http_status        INT           NULL,
    response_row_count INT           NOT NULL DEFAULT 0,
    file_path          TEXT          NULL,
    record_count       INT           NOT NULL DEFAULT 0,
    status             VARCHAR(10)   NOT NULL,
    error_message      TEXT          NULL,
    PRIMARY KEY (log_id)
);