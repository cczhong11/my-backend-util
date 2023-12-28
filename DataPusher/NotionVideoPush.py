from .DataPusherBase import DataPusherBase
from DataFetcher.MichelinDataFetcher import Restaurant
from notion_client import Client
from log_util import get_logger

logger = get_logger()


video2023 = "769be7a3ca674eb18d5e7a5126759dc1"


def notion_util(data, column_type):
    columns = {
        "title": {"title": [{"text": {"content": data}}]},
        "multi_select": {"type": "multi_select", "multi_select": [{"name": data}]},
        "url": {"type": "url", "url": data},
        "rich_text": {"rich_text": [{"text": {"content": data}}]},
        "number": {"number": data},
        "select": {"select": {"name": data}},
        "date": {"date": {"start": data}},
    }
    return columns[column_type]


class NotionVideoPush(DataPusherBase):
    def __init__(self, api, debug=False):
        self.bot = Client(auth=api)
        self.debug = debug

    def push_data(self, video_data, dst=video2023):
        if self.debug:
            print(f"send {dst}: {video_data}")
            return {}

        new_page_props = {
            "Name": notion_util(video_data["file_name"], "title"),
            "Description": notion_util(video_data["description"], "rich_text"),
            "Focal Length": notion_util(video_data["focal_length"], "rich_text"),
            "Duration": notion_util(video_data["duration"], "number"),
            "Size": notion_util(video_data["size"], "number"),
            "Tags": notion_util("default", "multi_select"),
        }
        self.bot.pages.create(parent={"database_id": dst}, properties=new_page_props)
        logger.info(f"send {dst}: {video_data}")
        return {"result": "success"}

    def get_current_data(self, topic):
        rs = {}

        return self.load_page()

    def update_page(self, pageid, **kwargs):
        self.bot.pages.update(pageid, **kwargs)

    def health_check(self):
        return True

    def load_page_get_key(self, content):
        return content["properties"]["Name"]["title"][0]["text"]["content"]

    def load_page_get_value(self, content):
        return content["id"]

    def load_page(self, pageid=video2023):
        rs = {}
        next_cursor = ""
        while True:
            if next_cursor == "":
                result = self.bot.databases.query(pageid, page_size=400)
            else:
                result = self.bot.databases.query(pageid, start_cursor=next_cursor)
            for r in result["results"]:
                try:
                    rs[self.load_page_get_key(r)] = self.load_page_get_value(r)
                except:
                    continue
            if not result["has_more"]:
                break
            next_cursor = result["next_cursor"]
        return rs
