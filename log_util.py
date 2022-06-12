import logging
import json
from constant import PATH
import os
from web_util import read_json_file

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
logging.basicConfig(
    filename=config[config_path],
    filemode="a",
    format="%(asctime)s,%(msecs)d %(name)s %(levelname)s %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S",
    level=logging.DEBUG,
)
logger = logging.getLogger()
