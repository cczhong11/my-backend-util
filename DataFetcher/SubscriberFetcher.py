import requests
from bs4 import BeautifulSoup
from .DataFetcherBase import DataFetcherBase
from web_util import parse_curl
import re


class SubscriberFetcher(DataFetcherBase):
    def __init__(self, cookie, topic, enable=True):
        self.topic = topic
        self.header = {}
        self.feedList = []
        super(SubscriberFetcher, self).__init__(cookie)

    def load_cookie(self):
        pass

    def get_data(self):
        if self.topic == "bilibili":
            return self.get_bilibili_data()
        if self.topic == "youtube":
            return self.get_youtube_data()
        if self.topic == "xiaohongshu":
            return self.get_xiaohongshu_data()

    def health_check(self):
        return True

    def get_bilibili_data(self, user_id="2935573"):
        result = requests.get(
            f"https://api.bilibili.com/x/relation/stat?vmid={user_id}&jsonp=jsonp"
        ).json()
        return {"follower": result["data"]["follower"], "name": "bilibili"}
