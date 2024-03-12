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
from DataWriter.SqliteDataWriter import SqliteDataWriter
import datetime
from dateutil.parser import parse

api = {}
with open(f"{PATH}/key.json") as f:
    api = json.load(f)

# SQL to create a new table called error_log
# with 5 columns: timestamp, user, cmd,stdout,return code
ERROR_LOG_SQL = """CREATE TABLE IF NOT EXISTS error_log (
    timestamp TEXT,
    user TEXT,
    cmd TEXT,
    stdout TEXT,
    return_code INTEGER
);"""

MONEY_LOG_SQL = """CREATE TABLE IF NOT EXISTS money_log (
    timestamp TEXT,
    description TEXT,
    amount float,
    category varchar(255)    
);
"""
from util import get_db_path, get_rss_path


rss_path = get_rss_path()
path = rss_path


def run_error_log():
    Gsheet = GoogleSheetReader(f"{PATH}/cookie/service_account.json", api["error_log"])
    cleaner = GoogleSheetPush(f"{PATH}/cookie/service_account.json", api["error_log"])
    data = Gsheet.get_data("Sheet1")

    writer = SqliteDataWriter(f"{path}/error_log.db", "error_log", ERROR_LOG_SQL)
    rs = writer.get_data("SELECT count(*) FROM error_log")

    for row in rs:
        current_count = row[0]
    for row in data:
        if row[0] == "":
            continue
        writer.write_data(
            f"{path}/error_log.db",
            "INSERT INTO error_log VALUES (?,?,?,?,?)",
            (row[0], row[1], row[2], row[3], row[4]),
        )
    rs = writer.get_data("SELECT count(*) FROM error_log")
    for row in rs:
        new_count = row[0]
    if new_count - current_count == len(data):
        print("new error log found")
        cleaner.clean_data()


def handle_datetime(date_str):
    try:
        date = parse(date_str)
        return date
    except ValueError:
        print(f"Cannot parse date string {date_str}")
        return None


def run_money_fetch():
    db_path = get_db_path() + "money_log.db"
    if not db_path:
        return
    sheet = GoogleSheetReader(
        f"{PATH}/cookie/service_account.json",
        api["money_sheet"],
    )
    data = sheet.get_data("archive")
    writer = SqliteDataWriter(db_path, "money_log", MONEY_LOG_SQL)
    rs = writer.get_data("SELECT timestamp,description FROM money_log")
    all_data = {str(row[0]) + row[1] for row in rs}

    for index, row in enumerate(data):
        if row[0] == "":
            print(index)
            continue
        date = handle_datetime(row[0])
        if str(date) + row[1] in all_data:
            print(f"row {index} already exists")
            continue
        date = handle_datetime(row[0])
        writer.write_data(
            db_path,
            "INSERT INTO money_log VALUES (?,?,?,?)",
            (date, row[1], row[2], row[3]),
        )


if __name__ == "__main__":
    run_error_log()
    # run_money_fetch()
