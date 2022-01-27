from constant import PATH
from DataReader.GoogleSheetReader import GoogleSheetReader
from DataPusher.TogglePush import TogglePush
import json
import sys
import os
from log_util import logger

api = {}
with open(f"{PATH}/key.json") as f:
    api = json.load(f)
project_map = {}
with open(f"{PATH}/cookie/toggle_project.json") as f:
    project_map = json.load(f)
    project_map = {i["name"]: i["id"] for i in project_map["data"]}


def get_shortcodes(gc):
    sheet = gc.get_data("Sheet3")
    rs = {}
    for row in sheet:
        if row[0] == "":
            continue
        rs[row[0]] = (row[1], row[2])
    return rs


def get_event(gc):
    event = gc.get_data("Sheet2")
    return event


def run():
    Gsheet = GoogleSheetReader(f"{PATH}/cookie/service_account.json", api["cal_sheet"])
    shortcodes = get_shortcodes(Gsheet)

    event = get_event(Gsheet)
    toggle = TogglePush(shortcodes, api["toggle_api"], project_map )
    toggle.push_data(event)


if __name__ == "__main__":
    try:
        run()
    except Exception as e:
        logger.exception(str(e))
