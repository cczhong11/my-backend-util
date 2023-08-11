from DataFetcher.AllTrailDataFetcher import Hike
from DataPusher.NotionPush import notion_util
from .DataPusherBase import DataPusherBase
from DataFetcher.MichelinDataFetcher import Restaurant
from notion_client import Client
from log_util import logger


all_trails_page = "25374a4d5915413c9534b7b66d8d4494"


class NotionAllTrailPush(DataPusherBase):
    def __init__(self, api, debug=False):
        self.bot = Client(auth=api)
        self.debug = debug

    def push_data(self, data):
        if self.debug:
            print(f"send {data}")
            return {}

        if not isinstance(data, Hike):
            logger.error("data is not Restaurant type")
            return {}
        new_page_props = {
            "Name": notion_util(data.name, "title"),
            "rating": notion_util(data.avg_rating, "number"),
            "city name": notion_util(data.city_name, "rich_text"),
            # "URL": notion_util(f"{data.url}", "url"),
            "Date": notion_util(str(data.created_at), "date"),
            "distance": notion_util(data.distance, "number"),
            "elevation": notion_util(data.elevation_gain, "number"),
            "lat": notion_util(data.lat, "number"),
            "lng": notion_util(data.lng, "number"),
            "trail_id": notion_util(data.trail_id, "number"),
        }
        self.bot.pages.create(
            parent={"database_id": all_trails_page}, properties=new_page_props
        )
        logger.info(f"send: {data}")
        return {"result": "success"}

    def get_current_data(self, topic):
        return self.load_page(all_trails_page, topic)

    def update_page(self, pageid, **kwargs):
        self.bot.pages.update(pageid, **kwargs)

    def health_check(self):
        return True

    def load_page_get_key(self, content):
        return (
            content["properties"]["name"]["title"][0]["plain_text"]
            + content["properties"]["trail_id"]["number"]
        )

    def load_page_get_value(self, content):
        return content["id"]

    def load_page(self, pageid):
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
