from DataFetcher.GMailDataFetcher import GMailDataFetcher, NewsLetterType
from DataWriter.RSSWriter import RSSWriter
from DataWriter.AWSS3DataWriter import AWSS3DataWriter
from log_util import logger
import os
from constant import PATH
import pickle
from datetime import datetime
from web_util import read_json_file
import pytz
import time_util


today = time_util.str_time(time_util.get_current_date(),"%Y/%m/%d")
yesterday = time_util.str_time(time_util.get_yesterday(),"%Y/%m/%d")

config = read_json_file(f"{PATH}/config.json")
os_name = os.uname().nodename
config_path = "rss_path"
if "MacBook" in os_name:
    config_path = "mac_rss_path"
api = read_json_file(f"{PATH}/key.json")
bucket = api["s3_rss_bucket"]


def run():
    gmail = GMailDataFetcher(f"{PATH}/cookie/gmail.json", f"{PATH}/cookie/gmailcredentials.json")
    s3 = AWSS3DataWriter(bucket)
    if not gmail.health_check() or s3.health_check():
        logger.exception("36kr health check failed")
    rss_writer = RSSWriter(config[config_path],"newsletter must read","https://study.tczhong.com", "news letter for tech worlds")
    rs = []
    for _, member in NewsLetterType.__members__.items():
        gmail.reset_query()
        gmail.set_sender(member)
        gmail.set_time(yesterday, today)
        tmp = gmail.get_data()
        rs.extend(gmail.analyze(member, tmp))
        
        
    for feed in rs:
        rss_writer.add_feed(feed['title'],feed['link'],feed['content'],feed['publishTime'])
    rss_writer.write_data("newsletter.xml","")
    s3.write_data("news", os.path.join(config[config_path], "newsletter.xml"))
if __name__ == '__main__':
    run()