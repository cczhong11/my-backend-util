from DataFetcher.AMCMovieDataFetcher import AMCMovieDataFetcher
from DataFetcher.DoubanFetcher import DoubanFetcher
from DataPusher.NotionPush import NotionPush, notion_util

from web_util import read_json_file
from constant import PATH
from log_util import get_logger

logger = get_logger()

import sys

items = []
with open("data/my_love.txt") as f:
    for l in f.readlines():
        items.append(l.strip())


def run():
    # health_check
    api = read_json_file(f"{PATH}/key.json")

    douban = DoubanFetcher(f"{PATH}/cookie/douban.cookie", "book")

    if not douban.health_check():
        logger.exception("douban health check failed")
        sys.exit(1)
    for item in items:
        douban_info = douban.get_data(item)
        print(douban_info["sid"])


if __name__ == "__main__":
    run()
