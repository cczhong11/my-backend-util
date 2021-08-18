from DataFetcher.News36krDataFetcher import News36krDataFetcher
from DataWriter.RSSWriter import RSSWriter
from DataWriter.AWSS3DataWriter import AWSS3DataWriter
from log_util import logger
import os
from constant import PATH
import pickle
from datetime import datetime
from web_util import read_json_file
import pytz


config = read_json_file(f"{PATH}/config.json")
os_name = os.uname().nodename
config_path = "rss_path"
if "MacBook" in os_name:
    config_path = "mac_rss_path"

def run():
    news = News36krDataFetcher("","")
    s3 = AWSS3DataWriter("rss-ztc")
    if not news.health_check():
        logger.exception("36kr health check failed")
    rss_writer = RSSWriter(config[config_path],"36kr must read","https://36kr.com/topics")
    data = news.get_data()
   
    for feed in data["data"]:
        rss_writer.add_feed(feed['title'],feed['link'],feed['content'],datetime.fromtimestamp(feed['publishTime']/1000, pytz.timezone("Asia/Shanghai")))
    rss_writer.write_data("36kr.xml","")
    s3.write_data("news", os.path.join(config[config_path], "36kr.xml"))
if __name__ == '__main__':
    run()