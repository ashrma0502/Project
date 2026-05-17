import sys
import os 

sys.path.append(os.path.join(os.path.dirname(__file__),'..','load'))

import load
def validate_bronze(indicators,bronze_logger):
    """
    Validate indicators of each country
    """
    bronze_logger.info("Step 5 — Running Bronze validation")
    REQUIRED_KEYS={"indicator","country","countryiso3code","date","value"}
    report=[]
    passed=True
    for country_name,indicator_data in indicators.items():
        for indicator_name,value in indicator_data.items():
            result={"country":    country_name,
                    "indicator":  indicator_name,
                    "http_ok":    False,
                    "metadata_ok":False,
                    "records_ok": False,
                    "keys_ok":    False,
                    "payload_ok": False,
                    "overall":    "PASS"}
            ok_audits=[a for a in value["Audit"] if a.get("http_status")==200]
            result["http_ok"]=len(ok_audits)>0
            if not result["http_ok"]:
                bronze_logger.error("Bronze FAIL as no HTTP 200 for %s's %s",country_name,indicator_name)
            result["metadata_ok"]=value["MetaData"] is not None
            if not result["metadata_ok"]:
                bronze_logger.error("Bronze FAIL as MetaData missing for %s's %s",country_name,indicator_name)
            non_null=[r for r in value["Records"] if r.get("data") is not None]
            result["records_ok"]=len(non_null)>0
            if not result["records_ok"]:
                bronze_logger.warning("Bronze WARN as no data records for %s's %s",country_name,indicator_name)
            bad_keys=[]
            for rec in non_null:
                d=rec.get("data") or {}
                missing=REQUIRED_KEYS-set(d.keys())
                if missing:
                    bad_keys.append(missing)
            result["keys_ok"]=len(bad_keys)==0
            if not result["keys_ok"]:
                if len(bad_keys)==1:
                    bronze_logger.warning("Bronze WARN for missing %d key in record for %s's %s: %s",len(bad_keys),country_name,indicator_name,bad_keys[0])
                else:
                    bronze_logger.warning("Bronze WARN for missing %d keys in record for %s's %s: %s",len(bad_keys),country_name,indicator_name,bad_keys[0])
            empty_200=[a for a in ok_audits if a.get("response_row_count",0)==0]
            result["payload_ok"]=len(empty_200)==0
            if not result["payload_ok"]:
                if len(empty_200)==1:
                    bronze_logger.warning("Bronze WARN for %d page as it returned HTTP 200 but zero rows for %s's %s",len(empty_200),country_name,indicator_name)
                else:
                    bronze_logger.warning("Bronze WARN for %d pages as it returned HTTP 200 but zero rows for %s's %s",len(empty_200),country_name,indicator_name)
            if not (result["http_ok"] and result["metadata_ok"]):
                result["overall"]="FAIL"
                passed=False
            elif not (result["records_ok"] and result["keys_ok"] and result["payload_ok"]):
                result["overall"]="WARN"
            report.append(result)
            bronze_logger.info("Bronze check %s for %s's %s",result["overall"],country_name,indicator_name)
    summary={k:sum(1 for r in report if r["overall"]==k)for k in ("PASS","WARN","FAIL")}
    bronze_logger.info("Bronze validation complete — PASS: %d | WARN: %d | FAIL: %d",summary["PASS"],summary["WARN"],summary["FAIL"])
    return passed,report

def validate_silver(country_df,indicator_df,fact_df,date_range,silver_logger):
    """
    Quality checks on the Silver DataFrames before MySQL load.
    """
    silver_logger.info("Step 9 — Running Silver data quality checks")
    passed=True
    report={}
    _,_,year_from,year_to=load.parse_date_range(date_range)
    if fact_df is None or fact_df.empty:
        silver_logger.error("Silver FAIL — fact table is empty")
        return False,{"fact_empty":True}
    null_iso3=int(fact_df["country_iso3"].isna().sum())
    null_code=int(fact_df["indicator_code"].isna().sum())
    report["null_country_iso3"]=null_iso3
    report["null_indicator_code"]=null_code
    if null_iso3>0 or null_code>0:
        silver_logger.error(
            "Silver FAIL as null keys: country_iso3=%d, indicator_code=%d",null_iso3,null_code)
        passed=False
    else:
        silver_logger.info("Silver PASS as no null country_iso3 or indicator_code")
    if year_from is not None:
        out=fact_df[(fact_df["year"]<year_from)|(fact_df["year"]>year_to)]
        report["year_out_of_range"]=len(out)
        if len(out)>0:
            silver_logger.error("Silver FAIL as %d rows outside year range %d:%d",len(out),year_from,year_to)
            passed=False
        else:
            silver_logger.info("Silver PASS as all years within %d:%d", year_from, year_to)
    else:
        out=fact_df[fact_df["year"] != year_to]
        report["year_out_of_range"]=len(out)
        if len(out)>0:
            silver_logger.error("Silver FAIL as %d rows outside year range %d:%d",len(out),year_from,year_to)
            passed=False
        else:
            silver_logger.info("Silver PASS as all years within %d:%d",year_from,year_to)
    bad=0
    for v in fact_df["indicator_value"].dropna():
        try:
            float(v)
        except (TypeError,ValueError):
            bad+=1
    report["non_numeric_values"]=bad
    if bad>0:
        silver_logger.error("Silver FAIL as %d non-numeric indicator_value entries",bad)
        passed=False
    else:
        silver_logger.info("Silver PASS as all non-null values are numeric")
    dups=int(fact_df.duplicated(subset=["country_iso3","indicator_code","year"]).sum())
    report["duplicate_keys"]=dups
    if dups>0:
        silver_logger.error("Silver FAIL as %d duplicate (country_iso3, indicator_code, year)",dups)
        passed=False
    else:
        silver_logger.info("Silver PASS as no duplicate natural keys")
    if country_df is not None and not country_df.empty:
        valid=set(country_df["iso3_code"].dropna())
        orphans=set(fact_df["country_iso3"].dropna())-valid
        report["orphan_countries"]=len(orphans)
        if orphans:
            silver_logger.warning("Silver WARN as %d country_iso3 not in country dim: %s",len(orphans),list(orphans))
        else:
            silver_logger.info("Silver PASS as all country_iso3 codes in country dim")
    if indicator_df is not None and not indicator_df.empty:
        valid=set(indicator_df["indicator_code"])
        orphans=set(fact_df["indicator_code"].dropna())-valid
        report["orphan_indicators"]=len(orphans)
        if orphans:
            silver_logger.warning("Silver WARN as %d indicator_codes not in indicator dim: %s",len(orphans),list(orphans))
        else:
            silver_logger.info("Silver PASS as all indicator_codes in indicator dim")
    completeness=(fact_df.groupby("indicator_code")["indicator_value"].apply(lambda s: round(s.notna().mean()*100,2)))
    report["completeness_pct"]=completeness.to_dict()
    for code,pct in completeness.items():
        silver_logger.info("Silver completeness — %s: %.2f non-null",code,pct)
    silver_logger.info("Silver validation complete — overall: %s","PASS" if passed else "FAIL")
    return passed,report
