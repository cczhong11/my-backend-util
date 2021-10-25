from DataFetcher.GMailDataFetcher import GMailDataFetcher, EmailType

from DataPusher.GoogleSheetPush import GoogleSheetPush
from Filter.GeneralFilter import GeneralFilter
from web_util import read_json_file
import time_util

from constant import PATH
from log_util import logger
import sys

today = time_util.str_time(time_util.get_current_date(), "%Y/%m/%d")
yesterday = time_util.str_time(time_util.get_yesterday(), "%Y/%m/%d")
#yesterday = "2021/09/01"


def run():
    # health_check
    debug = False
    api = read_json_file(f"{PATH}/key.json")
    gmail = GMailDataFetcher(
        f"{PATH}/cookie/gmail.json", f"{PATH}/cookie/gmailcredentials.json")
    moneyfilter = GeneralFilter(f"{PATH}/moneytype.yaml")
    sheet = GoogleSheetPush(f"{PATH}/cookie/service_account.json",
                            api["money_sheet"], "money", moneyfilter, debug)
    if not gmail.health_check():
        logger.exception("gmail health check failed")
        sys.exit(1)

    # get data
    for _, member in EmailType.__members__.items():
        gmail.reset_query()
        gmail.set_sender(member)
        gmail.set_time(yesterday, today)
        rs = gmail.get_data()
        analyze_rs = gmail.analyze(member, rs)
        for r in analyze_rs:
            print(r)
            if r is None or len(r) != 3:
                continue
            sheet.push_data(r)


if __name__ == '__main__':
    run()
