import requests
from bs4 import BeautifulSoup
from .DataFetcherBase import DataFetcherBase
from functools import lru_cache
import re
import json
from log_util import logger


class News36krDataFetcher(DataFetcherBase):
    def __init__(self, cookie, topic, run_feq="1h", enable=True):
        self.topic = topic
        self.header = {}
        self.feedList = []
        super(News36krDataFetcher, self).__init__(cookie, run_feq, enable)

    def load_cookie(self):
        pass

    @lru_cache(128)
    def extract_content(self, link):
        result = requests.get(f"https://36kr.com{link}").text
        res = re.findall(r'"articleDetailData":(.*?),"articleRecommendData":', result)
        if len(res) == 0:
            return ""
        res = res[0]
        res = json.loads(res)
        content = str(res.get("data", {}).get("widgetContent", ""))
        return content.replace("\xa0", " ").replace("\x08", "").replace(
            "\\t", ""
        ), res.get("data", {}).get("publishTime", 0)

    @lru_cache(128)
    def process_topic(self, link):
        result = requests.get(f"https://36kr.com{link}").content
        soup = BeautifulSoup(result, "lxml")
        feedList = soup.select("div.list-item-right")
        rs = []
        for feed in feedList:
            link = feed.select("a")[0].get("href")
            title = feed.select("a")[0].text
            content, publishTime = self.extract_content(link)
            if publishTime == 0:
                continue
            logger.info(f"process {title}")
            rs.append(
                {
                    "title": title,
                    "content": content,
                    "link": f"https://36kr.com{link}",
                    "publishTime": publishTime,
                }
            )
        return rs

    def get_data(self):
        feedRes = []
        result = requests.get(f"https://36kr.com/topics").content
        soup = BeautifulSoup(result, "lxml")
        feedList = soup.select("div.kr-shadow-content")
        if len(feedList) == 0:
            return {}
        for feed in feedList:
            link = feed.select("a")[0].get("href")
            title = feed.select("a")[0].select("div.flow-item-title")[0].text
            logger.info(f"topic: {title} link: {link}")
            if "一周" in title or "今日" in title:
                rs = self.process_topic(link)
                feedRes.extend(rs)
        return {"data": feedRes}

    def health_check(self):
        result = requests.get("https://36kr.com/topics").content
        soup = BeautifulSoup(result, "lxml")
        feedList = soup.select("div.kr-shadow-content")
        if len(feedList) == 0:
            return False
        return True
