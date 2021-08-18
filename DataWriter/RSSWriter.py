from DataWriter.DataWriterBase import DataWriterBase
import os
from feedgen.feed import FeedGenerator


class RSSWriter(DataWriterBase):
    def __init__(self, dst_folder:str, rss_title:str, rss_link:str, rss_description:str):
        super(RSSWriter, self).__init__()
        self.dst_folder = dst_folder
        self.fg = FeedGenerator()
        self.fg.title(rss_title)
        self.fg.author({"name":"tianchen", "email":"me@tczhong.com"})
        self.fg.link(href=rss_link)
        self.fg.language("CN")
        self.fg.description(rss_description)
        if "podcast" in rss_description:
            self.fg.load_extension('podcast')
            self.fg.podcast.itunes_category('Arts', 'Books')
            
    def add_feed(self, title, link, content,pubdate):
        fe = self.fg.add_entry()
        fe.title(title)
        fe.link(href=link)
        fe.content(content)
        fe.pubDate(pubdate)
    
    def add_podcast(self, title, link, pubdate):
        fe = self.fg.add_entry()
        fe.id(link)
        filename = title.split('.')[0]
        filename = filename.split('/')[-1]
        fe.title(filename)
        fe.description(title)
        fe.enclosure(link, 0, 'audio/mpeg')
        
    def write_data(self, path, data):
        self.fg.rss_file(f"{self.dst_folder}/{path}")
        
    def health_check(self) -> bool:
        if os.path.exists(self.dst_folder):
            return True
        return False