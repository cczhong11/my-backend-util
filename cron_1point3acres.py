from DataPusher.TelegramPush import TelegramPush
from constant import PATH
from DataFetcher.BBS1pointDataFetcher import BBS1pointDataFetcher
import json
import sys
import os
from log_util import get_logger

logger = get_logger()

api = {}
with open(f"{PATH}/key.json") as f:
    api = json.load(f)


def run():
    bot = TelegramPush(api["telegram_tuisongzhushou"], False)
    # run health check
    job = BBS1pointDataFetcher(f"{PATH}/cookie/1point3acres.cookie", "job")
    if not job.health_check():
        logger.exception("Job check failed")
        sys.exit(1)
    application = BBS1pointDataFetcher(
        f"{PATH}/cookie/1point3acres.cookie", "application"
    )
    if not application.health_check():
        logger.exception("Job check failed")
        sys.exit(1)
    # get data

    jobs = job.get_data()
    applications = application.get_data()

    # send data

    for feed in jobs:
        if "实习" not in feed:
            if "在职跳槽" in feed:
                bot.push_data(feed, "@usinterview")
            else:
                bot.push_data(feed, "@usnewgradinterview")
        else:
            bot.push_data(feed, "@usinterninterview")
    for feed in applications:
        bot.push_data(feed, "@usgradapplication")


if __name__ == "__main__":
    try:
        run()
    except Exception as e:
        logger.exception(str(e))
