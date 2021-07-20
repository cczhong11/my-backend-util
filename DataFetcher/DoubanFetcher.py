import requests
from bs4 import BeautifulSoup
from DataFetcherBase import DataFetcherBase
from web_util import parse_curl
import re

CAT_ID = {
    "movie": 1002
}



class DoubanFetcher(DataFetcherBase):
    def __init__(self, cookie, topic, run_feq="1h",enable=True):
        self.topic = topic
        self.header = {}
        self.feedList = []
        super(DoubanFetcher, self).__init__(cookie, run_feq, enable)
    
    def load_cookie(self):
        cookie_str = ""
        with open(self.cookie) as f:
            cookie_str = f.read()
        _,header = parse_curl(cookie_str)
        self.header = header
    
    def get_data(self, query):
        feedRes = {}
        result = requests.get(f"https://www.douban.com/search?cat={CAT_ID[self.topic]}&q={query}", headers=self.header).content
        soup = BeautifulSoup(result, "lxml")
        feedList = soup.findAll("div",attrs={"class":"content"})
        if len(feedList) == 0:
            return {}
        feed = feedList[0]
        href = feed.findAll("a")[0]
        rating = feed.findAll("span",attrs={"class":"rating_nums"})
        if len(rating) == 0:
            rating_nums = -1
        else:
            rating_nums = rating[0].text
        feedRes['href'] = href.get("href")
        feedRes['title'] = href.text
        feedRes['rating'] = rating_nums
        return feedRes
        
     
    def health_check(self):
        result = requests.get("https://www.douban.com/search?cat=1002&q=tt10327252", headers=self.header).content
        soup = BeautifulSoup(result, "lxml")
        feedList = soup.findAll("div",attrs={"class":"content"})
        
        if len(feedList) == 0:
            print("no feed list")
            return False
        return True

