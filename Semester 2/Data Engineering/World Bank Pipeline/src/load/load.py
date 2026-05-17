import os
import datetime
import json
from sqlalchemy import create_engine,text
from sqlalchemy.engine import URL
import pandas as pd

def parse_date_range(date_range):
    """
    Parse date-range string into year integers
    """
    if not date_range or not str(date_range).strip():
        raise ValueError("date_range must not be empty or None.")
    date_range=str(date_range).strip()
    def _to4(y_str):
        y=int(y_str)
        return y+2000 if y<100 else y
    def _year_from_token(token):
        token=token.strip()
        parts=token.split("-")
        if len(parts)==1:
            return _to4(parts[0])
        if len(parts)==3:
            if len(parts[0])>=4:
                return _to4(parts[0])
            if len(parts[2])>=4:
                return _to4(parts[2])
            t0,t2=int(parts[0]),int(parts[2])
            return _to4(parts[2]) if t0 <= t2 else _to4(parts[0])
        raise ValueError("Cannot extract a year from token '%s'. Expected YYYY, YYYY-MM-DD, or DD-MM-YYYY."%(token))
    if ":" not in date_range:
        try:
            year_to=_year_from_token(date_range)
        except (ValueError,IndexError) as exc:
            raise ValueError(f"Invalid single-date value '{date_range}': {exc}") from exc
        return None,date_range,None,year_to
    sides=date_range.split(":",1)
    raw_from,raw_to=sides[0].strip(),sides[1].strip()
    if not raw_from or not raw_to:
        raise ValueError("date_range '%s' has an empty side. Both from and to are required when ':' is present."%(date_range))
    try:
        year_from=_year_from_token(raw_from)
        year_to=_year_from_token(raw_to)
    except (ValueError,IndexError) as exc:
        raise ValueError(f"Cannot parse date range '{date_range}': {exc}") from exc
    if year_from>year_to:
        raise ValueError(f"date_from ({year_from}) must not be after date_to ({year_to}).")
    return raw_from,raw_to,year_from,year_to

def _run_sql_file(engine,sql_path,logger):
    """
    Read a .sql file from disk and execute every non-empty statement
    """
    with open(sql_path,"r") as f:
        content=f.read()
    statements=[s.strip() for s in content.split(";") if s.strip()]
    with engine.begin() as conn:
        for stmt in statements:
            conn.execute(text(stmt))
    logger.info("Executed SQL: %s having %d statements",os.path.basename(sql_path),len(statements))

def load_bronze_data(output,indicators,api,pipeline_run_id,bronze_logger):
    """
    Save Bronze extracted data as partitioned JSON batch files
    """
    bronze_logger.info("Starting Bronze load")
    batch_log=[]
    batch_size=output['bronze']['batch_size']
    _,_,year_from,year_to=parse_date_range(api['date_range'])
    for country,indicators_data in indicators.items():
        for indicator,value in indicators_data.items():
            bronze_logger.info("Loading %s's %s",country,indicator)
            dir_path=os.path.join('..',output['data'],output['bronze']['path'],output['bronze']['world_bank'],pipeline_run_id,country,indicator)
            os.makedirs(dir_path,exist_ok=True)
            metadata_path=os.path.join(dir_path,"MetaData.json")
            try:
                with open(metadata_path,"w") as f:
                    json.dump(value["MetaData"],f,indent=2)
                bronze_logger.info("Metadata written for %s",indicator)
            except Exception as e:
                bronze_logger.error("Failed writing MetaData for %s's %s: %s",country,indicator,e)
                continue
            audit_path=os.path.join(dir_path,"Audit.json")
            try:
                with open(audit_path,"w") as f:
                    json.dump(value["Audit"],f,indent=2)
                bronze_logger.info("Audit written for %s",indicator)
            except Exception as e:
                bronze_logger.error("Failed writing Audit for %s's %s: %s",country,indicator,e)
                continue
            records=[r for r in value["Records"] if r.get("data") is not None]
            if not records:
                bronze_logger.warning("No records for %s's %s",country,indicator)
                first_audit=value["Audit"][0] if value["Audit"] else {}
                batch_log.append({
                    "batch_id":          "000",
                    "pipeline_run_id":   pipeline_run_id,
                    "load_timestamp":    datetime.datetime.now().strftime('%Y-%m-%d %I:%M:%S %p'),
                    "country":           country,
                    "indicator_name":    indicator,
                    "indicator_code":    None,
                    "date_from":         int(year_from),
                    "date_to":           int(year_to),
                    "api_url":           first_audit.get("api_url"),
                    "http_status":       first_audit.get("http_status"),
                    "response_row_count":0,
                    "file_path":         None,
                    "record_count":      0,
                    "status":            "SUCCESS",
                    "error_message":     None})
                continue
            batch_count=1
            audit_map={a["page"]: a for a in value["Audit"]}
            for i in range(0,len(records),batch_size):
                batch=records[i:i+batch_size]
                file_path=os.path.join(dir_path,"Batch_%.3d.json"%(batch_count))
                load_date=datetime.datetime.now().strftime('%Y-%m-%d %I:%M:%S %p')
                status="SUCCESS"
                error_msg=None
                try:
                    with open(file_path,"w") as f:
                        json.dump(batch,f,indent=2)
                    bronze_logger.info("Saved batch_%.3d.json | records: %d",batch_count,len(batch))
                except Exception as e:
                    bronze_logger.error("Failed writing %s: %s",file_path,e)
                    status="FAILED"
                    error_msg=str(e)
                page=batch[0].get("page") if batch and isinstance(batch[0],dict) else None
                audit_data=audit_map.get(page, {})
                if not audit_data:
                    bronze_logger.warning("Missing audit data for %s page %s",indicator,page)
                batch_log.append({"batch_id":          "%.3d"%(batch_count),
                                  "pipeline_run_id":   pipeline_run_id,
                                  "load_timestamp":    load_date,
                                  "country":           country,
                                  "indicator_name":    indicator,
                                  "indicator_code":    batch[0].get("indicator") if batch and isinstance(batch[0],dict) else None,
                                  "date_from":         int(year_from),
                                  "date_to":           int(year_to),
                                  "api_url":           audit_data.get("api_url"),
                                  "http_status":       audit_data.get("http_status"),
                                  "response_row_count":audit_data.get("response_row_count",0),
                                  "file_path":         file_path,
                                  "record_count":      len(batch),
                                  "status":            status,
                                  "error_message":     error_msg})
                if status=="SUCCESS":
                    bronze_logger.info("Saved %s's %s | records: %d",country,indicator,len(batch))
                else:
                    bronze_logger.warning("Batch %03d FAILED for %s's %s",batch_count,country,indicator)
                batch_count+=1
    bronze_logger.info("Bronze load complete. Total batch log rows: %d",len(batch_log))
    return batch_log

def load_bronze_metadata(sql_server,batch_log,ddl_dir,bronze_logger):
    """
    Create bronze_ingestion_log from DDL and insert batch-log rows
    """
    url=URL.create(drivername='%s+%s'%(sql_server['dialect'],sql_server['driver']),
                   username=  sql_server['user'],
                   password=  sql_server['password'],
                   host=      sql_server['host'],
                   port=      sql_server['port'],
                   database=  sql_server['database'])
    engine=create_engine(url)
    ddl_file=os.path.join(ddl_dir, "bronze ingestion log.sql")
    _run_sql_file(engine,ddl_file,bronze_logger)
    bronze_logger.info("bronze_ingestion_log table ready.")
    if not batch_log:
        bronze_logger.warning("No batch_log rows to insert into bronze_ingestion_log.")
        return
    rows=[]
    for row in batch_log:
        r=dict(row)
        if isinstance(r.get("load_timestamp"),str):
            r["load_timestamp"]=datetime.datetime.strptime(r["load_timestamp"],'%Y-%m-%d %I:%M:%S %p')
        rows.append(r)
    with engine.begin() as conn:
        conn.execute(
            text("""INSERT INTO bronze_ingestion_log
                    (batch_id,pipeline_run_id,load_timestamp,country,indicator_name,indicator_code,date_from,date_to,api_url,http_status,response_row_count,
                     file_path,record_count,status,error_message)
                    VALUES
                    (:batch_id,:pipeline_run_id,:load_timestamp,:country,:indicator_name,:indicator_code,:date_from,:date_to,:api_url,:http_status,:response_row_count,
                     :file_path,:record_count,:status,:error_message)"""),rows)
    bronze_logger.info("Inserted %d rows into bronze_ingestion_log.",len(rows))

def load_silver_data(sql_server,country_df,indicator_df,calendar_df,fact_df,ddl_dir,silver_sql_dir,silver_logger):
    """
    Create Silver tables from DDL and load DataFrames via INSERT IGNORE
    """
    url=URL.create(drivername='%s+%s'%(sql_server['dialect'],sql_server['driver']),
                   username=  sql_server['user'],
                   password=  sql_server['password'],
                   host=      sql_server['host'],
                   port=      sql_server['port'],
                   database=  sql_server['database'])
    engine=create_engine(url)
    ddl_file=os.path.join(ddl_dir,"silver tables.sql")
    _run_sql_file(engine,ddl_file,silver_logger)
    silver_logger.info("Silver tables ready.")
    insert_sql_path=os.path.join(silver_sql_dir,"silver insert.sql")
    with open(insert_sql_path, "r") as f:
        insert_sql_content=f.read()
    stmts={}
    for block in insert_sql_content.split("-- TABLE:"):
        block=block.strip()
        if not block:
            continue
        first_line,_,rest=block.partition("\n")
        stmts[first_line.strip()]=rest.strip()

    def _load_df(df,table_name):
        if df is None or df.empty:
            silver_logger.warning("Skipping empty DataFrame for %s",table_name)
            return
        for col in df.columns:
            if "timestamp" in col and df[col].dtype==object:
                df[col]=pd.to_datetime(df[col],errors='coerce')
        rows=df.where(pd.notnull(df),None).to_dict(orient='records')
        stmt=stmts.get(table_name)
        if not stmt:
            silver_logger.error("No INSERT IGNORE statement found for %s",table_name)
            return
        with engine.begin() as conn:
            for i in range(0,len(rows),500):
                chunk=rows[i:i+500]
                conn.execute(text(stmt),chunk)
        silver_logger.info("Loaded %d rows into %s",len(rows),table_name)

    _load_df(country_df,  "silver_country_dim")
    _load_df(indicator_df,"silver_indicator_dim")
    _load_df(calendar_df, "silver_calendar_year")
    _load_df(fact_df,     "silver_indicator_fact")

def build_gold_marts(sql_server,ddl_dir,gold_sql_dir,gold_logger):
    """
    Create Gold tables and populate them from Silver via SQL files
    """
    url=URL.create(drivername='%s+%s'%(sql_server['dialect'],sql_server['driver']),
                   username=  sql_server['user'],
                   password=  sql_server['password'],
                   host=      sql_server['host'],
                   port=      sql_server['port'],
                   database=  sql_server['database'])
    engine=create_engine(url)
    ddl_file=os.path.join(ddl_dir,"gold tables.sql")
    _run_sql_file(engine,ddl_file,gold_logger)
    gold_logger.info("Gold tables DDL applied.")
    mart_file=os.path.join(gold_sql_dir,"gold marts.sql")
    _run_sql_file(engine,mart_file,gold_logger)
    gold_logger.info("Gold marts populated.")
