import logging
import os
from logging.handlers import RotatingFileHandler

def generate_logs(config,pipeline_run_id):
    """
    Create four separate named loggers, each backed by its own rotating log file inside a timestamped subfolder.
    """
    log_cfg=config['logging']
    level=getattr(logging,log_cfg['level'])
    formatter=logging.Formatter("%(asctime)s: %(levelname)s: %(message)s",datefmt="%Y-%m-%d %I:%M:%S %p")
    run_log_dir=os.path.join('..',config['output']['data'],config['output']['logs'],pipeline_run_id)
    os.makedirs(run_log_dir,exist_ok=True)
    files=log_cfg['log_files']

    def _make_logger(name):
        lg=logging.getLogger(name)
        lg.setLevel(level)
        lg.handlers.clear()
        lg.propagate=False
        if files[name]['log_to_file']:
            path=os.path.join(run_log_dir,files[name]['file'])
            fh=RotatingFileHandler(path,maxBytes=log_cfg['max_file_size_mb']*1024*1024,backupCount=log_cfg['backup_count'],encoding='utf-8')
            fh.setLevel(level)
            fh.setFormatter(formatter)
            lg.addHandler(fh)
        if files[name]['log_to_console']:
            console_handler=logging.StreamHandler()
            console_handler.setLevel(level)
            console_handler.setFormatter(formatter)
            lg.addHandler(console_handler)
        return lg

    bronze_log=_make_logger("bronze")
    silver_log=_make_logger("silver")
    gold_log=_make_logger("gold")
    summary_log=_make_logger("summary")

    return {"bronze":     bronze_log,
            "silver":     silver_log,
            "gold":       gold_log,
            "summary":    summary_log,
            "run_log_dir":run_log_dir}
