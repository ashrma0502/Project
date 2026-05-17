import datetime
import pandas as pd
import sys
import os

sys.path.append(os.path.join(os.path.dirname(__file__),'..','load'))

import load
def build_silver_country_dim(indicators,config_countries,silver_logger):
    """
    Build silver_country_dim
    """
    silver_logger.info("Step 6 — Building silver_country_dim")
    rows={}
    for key,val in config_countries.items():
        iso2=val.get('iso2code','').strip().upper()
        iso3=val.get('iso3code','').strip().upper()
        name=val.get('name','').strip()
        if iso2:
            rows[iso2]={"iso2_code":     iso2,
                        "iso3_code":     iso3 if iso3 else None,
                        "country_name":  name,
                        "region_name":   None,
                        "income_group":  None,
                        "is_active":     1,
                        "load_timestamp":datetime.datetime.now().strftime('%Y-%m-%d %I:%M:%S %p')}
    for country_name,indicator_data in indicators.items():
        for indicator_name,value in indicator_data.items():
            for rec in value["Records"]:
                if rec.get("data") is None:
                    continue
                d=rec["data"]
                iso2=d.get("country",{}).get("id","").strip().upper()
                name=d.get("country",{}).get("value","").strip()
                if iso2 and iso2 in rows and name:
                    rows[iso2]["country_name"]=name
    df=pd.DataFrame(list(rows.values()))
    if df.empty:
        silver_logger.warning("silver_country_dim is empty")
        return df
    df=df.drop_duplicates(subset=["iso2_code"]).reset_index(drop=True)
    silver_logger.info("silver_country_dim: %d rows",len(df))
    return df

def build_silver_indicator_dim(indicators,silver_logger):
    """
     Build silver_indicator_dim
    """
    silver_logger.info("Step 7 — Building silver_indicator_dim")
    rows={}
    for country_name,indicator_data in indicators.items():
        for indicator_name,value in indicator_data.items():
            for rec in value["Records"]:
                if rec.get("data") is None:
                    continue
                d=rec["data"]
                code=d.get("indicator",{}).get("id","").strip()
                name=d.get("indicator",{}).get("value",indicator_name).strip()
                unit=d.get("unit","").strip()
                if code and code not in rows:
                    rows[code]={"indicator_code":code,
                                "indicator_name":name,
                                "unit":          unit if unit else None,
                                "source_system": "World Bank API",
                                "load_timestamp":datetime.datetime.now().strftime('%Y-%m-%d %I:%M:%S %p')}
    df=pd.DataFrame(list(rows.values()))
    if df.empty:
        silver_logger.warning("silver_indicator_dim is empty")
        return df
    df=df.drop_duplicates(subset=["indicator_code"]).reset_index(drop=True)
    silver_logger.info("silver_indicator_dim: %d rows",len(df))
    return df

def build_silver_calendar_year(date_range,silver_logger):
    """
    Build silver_calendar_year
    """
    _,_,year_from,year_to=load.parse_date_range(date_range)
    if year_from is None:
        years=[year_to]
        year_from=year_to
    else:
        years=list(range(year_from,year_to+1))
    df=pd.DataFrame({"year":years})
    silver_logger.info("silver_calendar_year: %d rows (%d to %d)",len(df),year_from,year_to)
    return df

def build_silver_indicator_fact(indicators,pipeline_run_id,silver_logger):
    """
    Build silver_indicator_fact
    """
    silver_logger.info("Step 8 — Building silver_indicator_fact")
    rows=[]
    for country_name,indicator_data in indicators.items():
        for indicator_name,value in indicator_data.items():
            for rec in value["Records"]:
                if rec.get("data") is None:
                    continue
                d=rec["data"]
                iso2=d.get("country",{}).get("id","").strip().upper()
                iso3=d.get("countryiso3code","").strip().upper()
                ind_code=d.get("indicator",{}).get("id","").strip()
                date_str=d.get("date","")
                raw_val=d.get("value")
                unit=d.get("unit","")
                obs_stat=d.get("obs_status","")
                decimals=d.get("decimal")
                try:
                    year=int(date_str)
                except (TypeError,ValueError):
                    silver_logger.warning("Skipping invalid year '%s' for %s's %s",date_str,country_name,indicator_name)
                    continue
                if raw_val is None or raw_val=="":
                    indicator_value=None
                else:
                    try:
                        indicator_value=float(raw_val)
                    except (TypeError,ValueError):
                        indicator_value=None
                rows.append({"pipeline_run_id":    pipeline_run_id,
                            "indicator_code":     ind_code,
                            "country_iso2":       iso2 if iso2 else None,
                            "country_iso3":       iso3 if iso3 else None,
                            "year":               year,
                            "indicator_value":    indicator_value,
                            "unit":               unit if unit else None,
                            "obs_status":         obs_stat if obs_stat else None,
                            "decimals":           int(decimals) if decimals is not None else None,
                            "ingestion_timestamp":datetime.datetime.now().strftime('%Y-%m-%d %I:%M:%S %p')})
    if not rows:
        silver_logger.warning("silver_indicator_fact is empty")
        return pd.DataFrame()
    df=pd.DataFrame(rows)
    before=len(df)
    df=df.drop_duplicates(subset=["country_iso3","indicator_code","year"]).reset_index(drop=True)
    removed=before-len(df)
    if removed:
        silver_logger.info("Removed %d duplicate rows from silver_indicator_fact",removed)
    df=df.dropna(subset=["country_iso3","indicator_code"])
    silver_logger.info("silver_indicator_fact: %d rows",len(df))
    return df
 