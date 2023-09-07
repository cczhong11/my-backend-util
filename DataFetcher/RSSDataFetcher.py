from .DataFetcherBase import DataFetcherBase
import feedparser
from datetime import datetime, timezone


class RSSDataFetcher(DataFetcherBase):
    def __init__(self, url):
        # super().__init__(url)
        self.url = url
        self.feed = feedparser.parse(url)

    def fetch(self, last_time: datetime):
        rs = []
        for entry in self.feed.entries:
            published_time = datetime.strptime(
                entry.published, "%a, %d %b %Y %H:%M:%S %z"
            )
            if published_time > last_time.replace(tzinfo=timezone.utc):
                rs.append(entry)
        return rs

    def health_check(self):
        if self.feed.status != 200:
            return False
        return True
