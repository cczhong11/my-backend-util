from .DataFetcherBase import DataFetcherBase
import requests
import datetime

yesterday = datetime.datetime.now() - datetime.timedelta(days=1)


class ZhihuArticleFetcher(DataFetcherBase):
    def __init__(self, url, headers):
        self.url = url
        self.headers = headers
        self.result = None

    def get_data(self, cutoff_timestamp=yesterday.timestamp()):
        if not self.result:
            self.health_check()
        articles = []
        if self.result:
            for article in self.result["data"]:
                if article["created"] > int(cutoff_timestamp):
                    articles.append(article)
        return articles

    def health_check(self):
        req = requests.get(self.url, headers=self.headers)
        if req.status_code == 200:
            self.result = req.json()
            print(len(self.result["data"]))
            return True
        else:
            print(req.status_code)
            return False
