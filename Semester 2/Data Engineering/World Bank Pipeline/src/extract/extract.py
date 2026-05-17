import requests
import tqdm
from tqdm.contrib.logging import logging_redirect_tqdm
import datetime
import threading

def process_indicator(lock,country_name,country_code,indicator,indicators_dict,api,endpoints,completion_msgs,position,bronze_logger): 
    """
    Extract all pages for one country/indicator pair inside a Thread.
    """
    indicator_name=indicator['name']
    indicator_code=indicator['code']
    bronze_logger.info("Processing %s's %s",country_name,indicator_name)
    max_pages=None
    pages_extracted=0
    with logging_redirect_tqdm():
        session=requests.Session()
        try:
            for page in tqdm.tqdm(range(1,api['max_page']+1),desc=country_name+'-'+indicator_name,colour='green',dynamic_ncols=True,leave=False,position=position):
                if max_pages is not None and page>max_pages:
                    break
                timestamp=datetime.datetime.now().strftime('%Y-%m-%d %I:%M:%S %p')
                try:
                    url="%s%s/%s%s/%s?date=%s&format=%s&page=%s"%(api['base_url'],endpoints['country'],country_code,endpoints['indicator'],indicator_code,api['date_range'],api['format'],page)
                    data=None
                    for attempt in range(api['max_retries']):
                        try:
                            data=session.get(url,timeout=10)
                            break
                        except Exception:
                            bronze_logger.warning("Retry %d/%d for %s's %s on page %d",attempt+1,api['max_retries'],country_name,indicator_name,page)
                    else:
                        bronze_logger.error("Max retries failed for %s's %s on page %s",country_name,indicator_name,page)
                        raise Exception("Max retries failed for %s's %s on page %s"%(country_name,indicator_name,page))
                except Exception as e:
                    bronze_logger.error("Request failed for %s on page %d: %s",indicator_name,page,e)
                    raise
                if data.status_code!=200:
                    bronze_logger.error("HTTP %d for %s's %s on page %d: %s",data.status_code, country_name, indicator_name,page, data.reason)
                    with lock:
                        indicators_dict[indicator_name]["Audit"].append({"indicator_name":    indicator_name,
                                                                         "indicator_code":    indicator_code,
                                                                         "country":           country_name,
                                                                         "country_code":      country_code,
                                                                         "page":              page,
                                                                         "api_url":           url,
                                                                         "http_status":       data.status_code,
                                                                         "response_row_count":0,
                                                                         "timestamp":         timestamp,
                                                                         "date_range":        api['date_range']})
                    break
                try:
                    response=data.json()
                except Exception as e:
                    bronze_logger.error("JSON parse failed for %s's %s on page %d: %s",country_name,indicator_name,page,e)
                    with lock:
                        indicators_dict[indicator_name]["Audit"].append({"indicator_name":    indicator_name,
                                                                         "indicator_code":    indicator_code,
                                                                         "country":           country_name,
                                                                         "country_code":      country_code,
                                                                         "page":              page,
                                                                         "api_url":           url,
                                                                         "http_status":       data.status_code,
                                                                         "response_row_count":0,
                                                                         "timestamp":         timestamp,
                                                                         "date_range":        api['date_range']})
                    continue
                with lock:
                    if indicators_dict[indicator_name]["MetaData"] is None:
                        max_pages=int(response[0].get("pages",1))
                        indicators_dict[indicator_name]["MetaData"]={"indicator_name":      indicator_name,
                                                                     "indicator_code":      indicator_code,
                                                                     "country":             country_name,
                                                                     "country_code":        country_code,
                                                                     "total_records":       response[0].get("total"),
                                                                     "per_page":            response[0].get("per_page"),
                                                                     "total_pages":         max_pages,
                                                                     "pages_extracted":     0,
                                                                     "date_range":          api['date_range'],
                                                                     "extraction_timestamp":timestamp}
                if max_pages is None:
                    max_pages=int(response[0].get("pages",1))
                records=(response[1] if (response and len(response)>1 and response[1]) else [])
                local_records=[]
                local_audit=[]
                if records:
                    for record in records:
                            local_records.append({"indicator":   indicator_code,
                                                   "country":     country_name,
                                                   "country_code":country_code,
                                                   "page":        page,
                                                   "data":        record})
                else:
                    local_records.append({"indicator":   indicator_code,
                                          "country":     country_name,
                                          "country_code":country_code,
                                          "page":        page,
                                          "data":        None})
                local_audit.append({"indicator_name":    indicator_name,
                                    "indicator_code":    indicator_code,
                                    "country":           country_name,
                                    "country_code":      country_code,
                                    "page":              page,
                                    "api_url":           url,
                                    "http_status":       data.status_code,
                                    "response_row_count":len(records),
                                    "timestamp":         timestamp,
                                    "date_range":        api['date_range']})
                with lock:
                    indicators_dict[indicator_name]["Records"].extend(local_records)
                    indicators_dict[indicator_name]["Audit"].extend(local_audit)
                pages_extracted+=1
        finally:
            session.close()
    with lock:
        if indicators_dict[indicator_name]["MetaData"] is not None:
            indicators_dict[indicator_name]["MetaData"]["pages_extracted"]=pages_extracted
        total=len(indicators_dict[indicator_name]["Records"])
        completion_msgs.append("Completed Extraction of %s's %s | Total records: %d"%(country_name,indicator_name,total))
   
def extract_bronze_data(api,bronze_logger):
    """
    Extract raw World Bank indicator data for all configured countries.
    """
    bronze_logger.info("Starting data extraction")
    endpoints=api['endpoints']
    countries=endpoints['countries']
    indicators_config=endpoints['indicator_id']
    indicators={}
    for country_key,country_val in countries.items():
        country_code=country_val['iso2code']
        country_name=country_val['name']
        indicators[country_name]={}
        completion_msgs=[]
        threads=[]
        lock=threading.Lock()
        for i,indicator in enumerate(indicators_config.values()):
                indicator_name=indicator['name']
                indicators[country_name][indicator_name]={"MetaData":None,"Records":[],"Audit":[]}
                t=threading.Thread(target=process_indicator,args=(lock,country_name,country_code,indicator,indicators[country_name],api,endpoints,completion_msgs,i,bronze_logger),name="%s-%s"%(country_name,indicator['name']))
                threads.append(t)
                t.start()
        for thread in threads:
            thread.join()
        for msg in completion_msgs:
            bronze_logger.info(msg)
    return indicators
