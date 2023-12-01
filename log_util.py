import logging
import json
from constant import PATH
import os
from web_util import read_json_file
import time_util

logging.getLogger("boto3").setLevel(logging.CRITICAL)
logging.getLogger("botocore").setLevel(logging.CRITICAL)
logging.getLogger("nose").setLevel(logging.CRITICAL)
logging.getLogger("s3transfer").setLevel(logging.CRITICAL)

config = read_json_file(f"{PATH}/config.json")
os_name = os.uname().nodename
print(os_name)
config_path = "log_path"
if "tianchende" in os_name:
    config_path = "mac_log_path"
if "mbp" in os_name:
    config_path = "darwin_log_path"


def get_logger(project_name="", lvl=logging.DEBUG):
    date_str = time_util.str_time(time_util.get_current_date(), "%Y_%m_%d")
    if project_name == "":
        log_name = f"{date_str}_all_in_one.log"
    else:
        log_name = f"{date_str}_{project_name}.log"
    logging.basicConfig(
        filename=config[config_path] + log_name,
        filemode="a",
        format="%(asctime)s,%(msecs)d %(name)s %(levelname)s %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S",
        level=lvl,
    )
    logger = logging.getLogger(project_name)
    return logger


logger = get_logger()
