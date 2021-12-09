from constant import PATH
from DataFetcher.InoReaderDataFetcher import InoReaderDataFetcher
from DataPusher.GoogleSheetPush import GoogleSheetPush
import json
import sys
import os
from log_util import logger

api = {}
with open(f"{PATH}/key.json") as f:
    api = json.load(f)


def run():

    # run health check
    reader = InoReaderDataFetcher(f"{PATH}/cookie/inoreader.cookie", "sheet_clean_tag")

    sheet = GoogleSheetPush(
        f"{PATH}/cookie/service_account.json",
        api["inoreader_sheet"],
        "sheet_clean_tag",
        None,
        False,
    )
    items = sheet.get_tags()

    if not reader.health_check():
        logger.exception("reader check failed")
        sys.exit(1)

    # filter the starred items and get tag-> article list
    items_dict = reader.find_articles_from_list(items)

    # send data
    reader.add_tags(items_dict)
    sheet.clean_data(items)


if __name__ == "__main__":
    try:
        run()
    except Exception as e:
        logger.exception(str(e))
