import requests
from bs4 import BeautifulSoup
from .DataFetcherBase import DataFetcherBase
from inoreader.main import get_client
import re

class InoReaderDataFetcher(DataFetcherBase):
    def __init__(self, cookie, topic, run_feq="1h",enable=True):
        self.topic = topic
        self.header = {}
        self.client = get_client(cookie)
        self.articles = []
        super(InoReaderDataFetcher, self).__init__(cookie, run_feq, enable)
    
    def load_cookie(self):
        pass
    
    def get_data(self, tag):
        filter_articles = []
        for article in self.articles:
            if tag in article.categories: 
                filter_articles.append(article)
        return filter_articles

    def starrd_hahaha_process(self):
        starred_hahaha = []
        for article in self.articles:
            if "user/1004680968/label/让自己开心一点" in article.categories:
                starred_hahaha.append(article)
        self.add_tag(starred_hahaha, "user/-/label/hahaha")
        self.remove_tag(starred_hahaha, "user/-/state/com.google/starred")
        pic = []
        for article in starred_hahaha:
            soup = BeautifulSoup(article.content)
            for img in soup.select("img"):
                pic.append(img.get("src"))
        return pic
    
    def remove_tag(self, articles, tag):
        if "starred" in tag:
            self.client.remove_starred(articles)
    
    def add_tag(self, articles,tag):
        self.client.add_tag(articles,tag)
    
    def health_check(self):
        if self.topic == 'star':
            articles_gen = self.client.get_stream_contents("user/-/state/com.google/starred")
        else:
            articles_gen = self.client.fetch_articles(tags=[self.topic])
        for article in articles_gen:
            self.articles.append(article)
        if len(self.articles) == 0:
            print("no feed list")
            return False
        return True

