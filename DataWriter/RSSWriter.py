from DataWriter.DataWriterBase import DataWriterBase
import os
from feedgen.feed import FeedGenerator

from util import get_tts_path

LOCAL_PATH = get_tts_path()


class RSSWriter(DataWriterBase):
    def __init__(
        self, dst_folder: str, rss_title: str, rss_link: str, rss_description: str
    ):
        super(RSSWriter, self).__init__()
        self.dst_folder = dst_folder
        self.fg = FeedGenerator()
        self.fg.title(rss_title)
        self.fg.author({"name": "tianchen", "email": "me@tczhong.com"})
        self.fg.link(href=rss_link)
        self.fg.language("CN")
        self.fg.description(rss_description)
        if "podcast" in rss_description:
            self.fg.load_extension("podcast")
            self.fg.podcast.itunes_category("Arts", "Books")

    def add_feed(self, title, link, content, pubdate):
        fe = self.fg.add_entry()
        fe.title(title)
        fe.link(href=link)
        fe.content(content)
        fe.pubDate(pubdate)

    def add_podcast(self, title, link, pubdate, content=None):
        fe = self.fg.add_entry()
        fe.id(link)
        filename = title.split(".")[0]
        filename = filename.split("/")[-1]
        desc = self.get_local_desc(filename, LOCAL_PATH)
        fe.title(filename)
        if content is not None:
            fe.description(content)
        elif desc != "":
            if len(desc) > 2000:
                desc = desc[:2000] + "..."
            fe.description(desc)
        else:
            fe.description(title)
        fe.pubDate(pubdate)
        fe.enclosure(link, 0, "audio/mpeg")

    def write_data(self, path, data):
        self.fg.rss_file(f"{self.dst_folder}/{path}")

    def health_check(self) -> bool:
        if os.path.exists(self.dst_folder):
            return True
        return False

    def get_local_desc(self, filename, path):
        if not os.path.exists(os.path.join(path, f"{filename}.txt")):
            return ""
        with open(os.path.join(path, f"{filename}.txt")) as f:
            return f.read()
