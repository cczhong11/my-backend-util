from DataReader.AWSS3DataReader import AWSS3DataReader
from DataWriter.RSSWriter import RSSWriter
from DataWriter.AWSS3DataWriter import AWSS3DataWriter
from log_util import get_logger

logger = get_logger()

import os
from constant import PATH
import urllib.parse
from web_util import read_json_file
import pytz


from util import get_rss_path


rss_path = get_rss_path()
api = read_json_file(f"{PATH}/key.json")
bucket = api["s3_rss_bucket"]


def run():
    s3_reader = AWSS3DataReader(bucket)
    s3_writer = AWSS3DataWriter(bucket)
    if not s3_reader.health_check() or not s3_writer.health_check():
        logger.exception("aws health check failed")
    rss_writer = RSSWriter(
        rss_path,
        "my articles to listen",
        "https://study.tczhong.com",
        "podcast: my article to listen",
    )
    data = s3_reader.get_data("articles", ".mp3", 5000)
    for feed in data:
        link = f"https://{bucket}.s3.amazonaws.com/{urllib.parse.quote(feed['Key'])}"
        rss_writer.add_podcast(feed["Key"], link, feed["LastModified"])
    rss_writer.write_data("articles_podcast.xml", "")
    s3_writer.write_data("articles", os.path.join(rss_path, "articles_podcast.xml"))

    rss_writer2 = RSSWriter(
        rss_path,
        "my daily news to listen",
        "https://study.tczhong.com",
        "podcast: my news to listen",
    )
    data = s3_reader.get_data("daily", ".mp3", 5000)
    for feed in data:
        link = f"https://{bucket}.s3.amazonaws.com/{urllib.parse.quote(feed['Key'])}"
        rss_writer2.add_podcast(feed["Key"], link, feed["LastModified"])
    rss_writer2.write_data("daily_news_podcast.xml", "")
    s3_writer.write_data("daily", os.path.join(rss_path, "daily_news_podcast.xml"))


if __name__ == "__main__":
    run()
