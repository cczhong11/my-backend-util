from constant import PATH
from DataFetcher.InoReaderDataFetcher import InoReaderDataFetcher
from DataPusher.GoogleSheetPush import GoogleSheetPush
import json
import sys
import os
from log_util import get_logger

logger = get_logger()


api = {}
with open(f"{PATH}/key.json") as f:
    api = json.load(f)


def run():
    # run health check
    reader = InoReaderDataFetcher(f"{PATH}/cookie/inoreader.cookie", "get_tag")

    sheet = GoogleSheetPush(
        f"{PATH}/cookie/service_account.json",
        api["inoreader_backup_sheet"],
        "write_tag",
        None,
        False,
    )
    if not reader.health_check():
        logger.exception("reader check failed")
        sys.exit(1)
    tags = reader.get_tags()
    for t in tags:
        print(t["name"])
        if "resource_" not in t["name"] and "area_" not in t["name"]:
            continue
        articles = reader.get_articles_from_tag(t["name"])

        sheet.write_tag_articles(t["name"], articles)
        logger.info("write tag %s", t["name"])


if __name__ == "__main__":
    try:
        run()
    except Exception as e:
        logger.exception(str(e))
