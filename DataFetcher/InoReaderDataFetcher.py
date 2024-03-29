import requests
from bs4 import BeautifulSoup
from .DataFetcherBase import DataFetcherBase
from inoreader.main import get_client
import re

# install git@github.com:cczhong11/python-inoreader.git


class InoReaderDataFetcher(DataFetcherBase):
    def __init__(self, cookie, topic, run_feq="1h", enable=True):
        self.topic = topic
        self.header = {}
        self.client = get_client(cookie)
        self.articles = []
        self.link_to_articles = {}
        super(InoReaderDataFetcher, self).__init__(cookie, run_feq, enable)

    def load_cookie(self):
        pass

    def get_data(self, tag):
        filter_articles = []
        for article in self.articles:
            if tag in article.categories:
                filter_articles.append(article)
        return filter_articles

    def find_articles_with_tag(self, tag):
        articles = []
        for r in self.client.get_stream_contents(f"user/-/label/{tag}"):

            articles.append(r)
        self.articles = articles

    def find_articles_from_list(self, items):
        new_rs = {}
        for tag in items:
            new_rs[tag] = []
            for link in items[tag]:
                if link in self.link_to_articles:
                    new_rs[tag].append(self.link_to_articles[link])
        return new_rs  # tag to articles

    def starrd_hahaha_process(self):
        starred_hahaha = []
        for article in self.articles:
            if "user/1004680968/label/让自己开心一点" in article.categories:
                starred_hahaha.append(article)
        self.add_tag(starred_hahaha, "hahaha")
        self.remove_tag(starred_hahaha, "user/-/state/com.google/starred")
        pic = []
        for article in starred_hahaha:
            soup = BeautifulSoup(article.content, "lxml")
            try:
                atag = soup.select("a")
                if len(atag) > 0:
                    link = soup.select("a")[0].get("href")
                    if "gif" in link:
                        pic.append(link)
                        continue
                for img in soup.select("img"):
                    pic.append(img.get("src"))
            except:
                continue
        return pic

    def remove_tag(self, articles, tag):
        if "starred" in tag:
            self.client.remove_starred(articles)

    def add_tags(self, items):
        for tag, articles in items.items():
            self.add_tag(articles, tag)
            self.remove_tag(articles, "starred")

    def add_tag(self, articles, tag):
        self.client.add_tag(articles, tag)

    def health_check(self):
        if self.topic == "star" or "sheet_clean" in self.topic:
            articles_gen = self.client.get_stream_contents(
                "user/-/state/com.google/starred"
            )
        else:
            return True

        for article in articles_gen:
            self.link_to_articles[article.link] = article
            self.articles.append(article)
        if len(self.articles) == 0:
            print("no feed list")
            return False
        return True

    def get_tags(self):
        tags = self.client.get_tags()
        return tags

    def get_articles_from_tag(self, tag):
        articles = self.client.get_stream_contents(f"user/-/label/{tag}")
        return [r for r in articles]
