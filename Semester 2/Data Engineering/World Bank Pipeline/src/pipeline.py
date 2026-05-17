import yaml
import os
import datetime
import sys

BASE_DIR=os.path.dirname(os.path.abspath(__file__))
sys.path.append(os.path.join(BASE_DIR,'extract'))
sys.path.append(os.path.join(BASE_DIR,'load'))
sys.path.append(os.path.join(BASE_DIR,'utils'))
sys.path.append(os.path.join(BASE_DIR,'transform'))
sys.path.append(os.path.join(BASE_DIR,'quality'))

import extract
import load
import utils
import transform
import quality

def run_pipeline():
    """
    Execute the entire pipeline
    """
    start_time=datetime.datetime.now()
    with open(os.path.join('..','config','config.yaml')) as config:
        DATA=yaml.safe_load(config)

    pipeline_run_id=start_time.strftime('%Y-%m-%d_%I-%M-%S_%p')
    loggers=utils.generate_logs(DATA,pipeline_run_id)
    bronze_log=loggers["bronze"]
    silver_log=loggers["silver"]
    gold_log=loggers["gold"]
    summary_log=loggers["summary"]
    run_log_dir=loggers['run_log_dir']
    api=DATA['api']
    output=DATA['output']
    sql_server=DATA['sql_server']
    sql_dir=output['sql']
    ddl_dir=os.path.join('..',sql_dir['base'],sql_dir['sql_ddl'])
    silver_dir=os.path.join('..',sql_dir['base'],sql_dir['sql_silver'])
    gold_sql_dir=os.path.join('..',sql_dir['base'],sql_dir['sql_gold'])
    step_times={}
    bronze_batch_logs=[]
    bronze_log.info("="*100)
    bronze_log.info("Pipeline started | run_id: %s",pipeline_run_id)
    bronze_log.info("="*100)

    try:
        bronze_log.info("STEP 1-3 — Extraction")
        start1=datetime.datetime.now()
        indicators=extract.extract_bronze_data(api,bronze_log)
        bronze_log.info("Extraction complete | Countries: %d",len(indicators))
        end1=datetime.datetime.now()
        step_times["STEPS 1-3 Extraction"]=(end1-start1,"OK")

        bronze_log.info("STEP 4 — Bronze file load")
        start2=datetime.datetime.now()
        bronze_batch_logs=load.load_bronze_data(output,indicators,api,pipeline_run_id,bronze_log)
        bronze_log.info("Bronze files written. Batch log rows: %d",len(bronze_batch_logs))
        end2=datetime.datetime.now()
        step_times["STEP 4 Bronze files"]=(end2-start2,"OK")

        bronze_log.info("STEP 5 — bronze_ingestion_log to SQL")
        start3=datetime.datetime.now()
        load.load_bronze_metadata(sql_server,bronze_batch_logs,ddl_dir,bronze_log)
        bronze_log.info("Bronze metadata persisted to %s.",sql_server['dialect'].title())
        end3=datetime.datetime.now()
        step_times["STEP 5 Bronze SQL"]=(end3-start3,"OK")

        bronze_log.info("STEP 6 — Bronze validation")
        start4=datetime.datetime.now()
        bronze_ok,bronze_report=quality.validate_bronze(indicators,bronze_log)
        if not bronze_ok:
            bronze_log.error("Bronze validation FAILED | Report: %s",bronze_report)
            end4=datetime.datetime.now()
            step_times["STEP 6 Bronze validation"]=(end4-start4,"FAILED")
            raise Exception("Bronze validation failed")
        else:
            bronze_log.info("Bronze validation PASSED.")
        end4=datetime.datetime.now()
        step_times["STEP 6 Bronze validation"]=(end4-start4,"OK")
    
        silver_log.info("STEP 7 — Build Silver country dimension")
        start5=datetime.datetime.now()
        country_df=transform.build_silver_country_dim(indicators,api['endpoints']['countries'],silver_log)
        silver_log.info("Country dimension built | rows: %d",len(country_df))

        silver_log.info("STEP 8a — Build Silver indicator dimension")
        indicator_df=transform.build_silver_indicator_dim(indicators,silver_log)
        silver_log.info("Indicator dimension built | rows: %d",len(indicator_df))

        silver_log.info("STEP 8b — Build Silver calendar dimension")
        calendar_df=transform.build_silver_calendar_year(api['date_range'],silver_log)
        silver_log.info("Calendar dimension built | rows: %d",len(calendar_df))
    
        silver_log.info("STEP 9 — Build Silver fact table")
        fact_df=transform.build_silver_indicator_fact(indicators,pipeline_run_id,silver_log)
        silver_log.info("Fact table built | rows: %d",len(fact_df))
        end5=datetime.datetime.now()
        step_times["STEPS 7—9 Silver transform"]=(end5-start5,"OK")

        silver_log.info("STEP 10 — Silver validation")
        start6=datetime.datetime.now()
        silver_ok,silver_report=quality.validate_silver(country_df,indicator_df,fact_df,api['date_range'],silver_log)
        if not silver_ok:
            silver_log.error("Silver validation FAILED | Report: %s",silver_report)
            end6=datetime.datetime.now()
            step_times["STEP 10 Silver validation"]=(end6-start6,"FAILED")
            raise Exception("Silver validation failed")
        else:
            silver_log.info("Silver validation PASSED.")
        end6=datetime.datetime.now()
        step_times["STEP 10 Silver validation"]=(end6-start6,"OK")

        silver_log.info("STEP 11 — Load Silver to %s",sql_server['dialect'].upper())
        start7=datetime.datetime.now()
        load.load_silver_data(sql_server,country_df,indicator_df,calendar_df,fact_df,ddl_dir,silver_dir,silver_log)
        silver_log.info("Silver tables loaded into %s",sql_server['dialect'].upper())
        end7=datetime.datetime.now()
        step_times["STEP 11 Silver SQL"]=(end7-start7,"OK")

        gold_log.info("STEPS 12-14 — Building Gold marts")
        start8=datetime.datetime.now()
        load.build_gold_marts(sql_server,ddl_dir,gold_sql_dir,gold_log)
        gold_log.info("Gold marts built successfully.")
        end8=datetime.datetime.now()
        step_times["STEPS 12-14 Gold build"]=(end8-start8,"OK")
        gold_log.info("STEP 15 — Pipeline complete | run_id: %s",pipeline_run_id)
    except Exception as e:
        bronze_log.exception("Pipeline FAILED due to error: %s",e)
        summary_log.error("Pipeline status: FAILED")
        return {"success":False,
                "run_id": pipeline_run_id,
                "log_dir":os.path.abspath(run_log_dir),
                "gold_df":None,
                "error":  str(e)}

    end_time=datetime.datetime.now()
    total_duration=(end_time-start_time).total_seconds()
    summary_log.info('='*100)
    summary_log.info("PIPELINE SUMMARY | run_id: %s",pipeline_run_id)
    summary_log.info('='*100)
    summary_log.info("Start          : %s",start_time.strftime('%Y-%m-%d %I:%M:%S %p'))
    summary_log.info("End            : %s",end_time.strftime('%Y-%m-%d %I:%M:%S %p'))
    summary_log.info("Duration       : %.2f seconds",total_duration)
    summary_log.info("Bronze batches : %d",len(bronze_batch_logs))
    summary_log.info('='*100)
    for step_name,(elapsed,status) in step_times.items():
        summary_log.info("%-50s : %s (%.2fs)",step_name,status,elapsed.total_seconds())
    summary_log.info('='*100)
    summary_log.info("Overall status : SUCCESS")
    summary_log.info('='*100)
    bronze_log.info("Pipeline finished successfully | duration: %.2f seconds",total_duration)
    bronze_log.info("Total batches created: %d",len(bronze_batch_logs))
    bronze_log.info('='*100)
    
if __name__=='__main__':
    result=run_pipeline()