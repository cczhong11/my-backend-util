from DataPusher.GoogleSheetPush import GoogleSheetPush
from DataReader.GoogleSheetReader import GoogleSheetReader
from constant import PATH
from web_util import read_json_file
import json
import os
from sqlite_util import (
    create_datebase,
    select_database,
    insert_database,
    update_database,
)

api = {}
with open(f"{PATH}/key.json") as f:
    api = json.load(f)

# SQL to create a new table called error_log
# with 5 columns: timestamp, user, cmd,stdout,return code
SQL = """CREATE TABLE IF NOT EXISTS error_log (
    timestamp TEXT,
    user TEXT,
    cmd TEXT,
    stdout TEXT,
    return_code INTEGER
);"""

config = read_json_file(f"{PATH}/config.json")
os_name = os.uname().nodename
config_path = "rss_path"
if "MacBook" in os_name:
    config_path = "mac_rss_path"
if "mbp" in os_name:
    config_path = "darwin_rss_path"
path = config[config_path]


def create_table():
    if not os.path.exists(f"{path}/error_log.db"):
        create_datebase(f"{path}/error_log.db", SQL)


def run():
    Gsheet = GoogleSheetReader(f"{PATH}/cookie/service_account.json", api["error_log"])
    cleaner = GoogleSheetPush(f"{PATH}/cookie/service_account.json", api["error_log"])
    data = Gsheet.get_data("Sheet1")
    create_table()
    rs = select_database(f"{path}/error_log.db", "SELECT count(*) FROM error_log")
    for row in rs:
        current_count = row[0]
    for row in data:
        if row[0] == "":
            continue

        insert_database(
            f"{path}/error_log.db",
            "INSERT INTO error_log VALUES (?,?,?,?,?)",
            (row[0], row[1], row[2], row[3], row[4]),
        )
    rs = select_database(f"{path}/error_log.db", "SELECT count(*) FROM error_log")
    for row in rs:
        new_count = row[0]
    if new_count - current_count == len(data):
        print("new error log found")
        cleaner.clean_data()


if __name__ == "__main__":
    run()
