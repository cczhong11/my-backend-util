from .DataPusherBase import DataPusherBase
from DataFetcher.MichelinDataFetcher import Restaurant
from notion_client import Client
from log_util import logger
AMC_DB = "d0ed80f8b0ce4d8bb6aa4c6e6bfeaa6c"
Restaurant_DB = "788b62b740ed41ce8827fd3e03ee4b97"


def notion_util(data, column_type):
    columns = {
        "title": {'title': [{'text': {'content': data}}]},
        "multi_select": {'type': 'multi_select', 'multi_select': [{'name': data}]},
        "url": {"type": 'url', 'url': data},
        'rich_text': {"rich_text": [{"text": {"content": data}}]},
        'number': {'number': data},
        'select': {'select':{
            "name": data
        }}
    }
    return columns[column_type]


class NotionPush(DataPusherBase):
    def __init__(self, api, debug=False):
        self.bot = Client(auth=api)
        self.debug = debug

    def push_data(self, data, dst):
        if self.debug:
            print(f"send {dst}: {data}")
            return {}
        if dst == "AMC":
            new_page_props = {
                'Title': notion_util(data['name'], 'title'),
                'Genre': notion_util(data['genre'], 'multi_select'),
                'imdb':  notion_util(f'https://www.imdb.com/title/{data["imdb"]}', 'url'),
                'douban_url': notion_util(data['douban_url'], 'url'),
                'chinese_name': notion_util(data['chinese_name'], 'rich_text'),
                'douban': notion_util(data['douban'], 'number'),
                'Link': notion_util(data['url'], 'url'),
            }
            self.bot.pages.create(
                parent={'database_id': AMC_DB},
                properties=new_page_props)

        if dst == "michelin":
            if not isinstance(data, Restaurant):
                logger.error("data is not Restaurant type")
                return {}
            new_page_props = {
                'Title': notion_util(data.name, 'title'),
                'Type': notion_util(data.cuisine_type, 'multi_select'),
                'City': notion_util(data.city, 'multi_select'),
                'URL':  notion_util(f'https://guide.michelin.com/{data.url}', 'url'),
                'OnlineBooking': notion_util(str(data.online_booking), 'rich_text'),
                'street_address': notion_util(data.street_address, 'rich_text'),
                'award': notion_util(data.award, 'multi_select'),
                'yelp_rating': notion_util(data.yelp_rating, 'number'),
                'yelp_link': notion_util(data.yelp_link, 'url'),
                'price': notion_util(data.price, 'select'), }
            self.bot.pages.create(
                parent={'database_id': Restaurant_DB},
                properties=new_page_props)
        logger.info(f"send {dst}: {data}")
        return {"result": "success"}

    def get_current_data(self, topic):
        rs = {}
        if topic == 'AMC':
            result = self.bot.databases.query(AMC_DB,page_size=400)
            for r in result['results']:
                try:
                    rs[r['properties']['Title']['title']
                        [0]['text']['content']] = (r['id'],r['properties'].get("douban",{}).get("number",-1))
                except:
                    continue
        if topic == 'michelin':
            next_cursor = ""
            while True:
                if next_cursor == "":
                    result = self.bot.databases.query(Restaurant_DB, page_size=400)
                else:
                    result = self.bot.databases.query(Restaurant_DB, start_cursor=next_cursor)
                for r in result['results']:
                    try:
                        rs[r['properties']['Title']['title']
                        [0]['text']['content']] = (r['id'],r['properties'].get("yelp_rating",{}).get("number",-1))
                    except:
                        continue
                if not result['has_more']:
                    break
                next_cursor = result['next_cursor']
        return rs

    def update_page(self, pageid, **kwargs):
        self.bot.pages.update(pageid, **kwargs)

    def health_check(self):
        return True
