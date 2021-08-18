from DataReader.AWSS3DataReader import AWSS3DataReader
from DataWriter.RSSWriter import RSSWriter
from DataWriter.AWSS3DataWriter import AWSS3DataWriter
from log_util import logger
import os
from constant import PATH
import urllib.parse
from datetime import datetime
from web_util import read_json_file
import pytz


config = read_json_file(f"{PATH}/config.json")
os_name = os.uname().nodename
config_path = "rss_path"
if "MacBook" in os_name:
    config_path = "mac_rss_path"
api = read_json_file(f"{PATH}/key.json")
bucket = api["s3_rss_bucket"]


def run():
    s3_reader = AWSS3DataReader(bucket)
    s3_writer = AWSS3DataWriter(bucket)
    if not s3_reader.health_check() or not s3_writer.health_check():
        logger.exception("aws health check failed")
    rss_writer = RSSWriter(config[config_path],"my book to listen","https://study.tczhong.com", "podcast: my book to listen")
    data = s3_reader.get_data('book', '.mp3')
    for feed in data:
        link = f"https://{bucket}.s3.amazonaws.com/{urllib.parse.quote(feed['Key'])}"
        rss_writer.add_podcast(feed['Key'],link,feed['LastModified'])
    rss_writer.write_data("book_podcast.xml","")
    s3_writer.write_data("book", os.path.join(config[config_path], "book_podcast.xml"))


if __name__ == '__main__':
    run()