from DataReader.SqliteDBReader import SqliteDBReader
from DataPusher.NotionPush import NotionPush, notion_util
from web_util import read_json_file
from log_util import logger

from constant import PATH
class NotionItem:
    def __init__(self, name, url, star, fork,language, description,available:bool,last_update,item_type):
        self.name = name
        self.url = url
        self.star = star
        self.fork = fork
        self.language = language
        self.description = description if description else ""
        self.available = available
        self.last_update = last_update
        self.item_type = item_type
        if len(self.description)>1000:
            self.description = self.description[:1000]
    def __str__(self):
        return f"{self.name} {self.url} {self.star} {self.fork} {self.language} {self.description} {self.available} {self.last_update} {self.item_type}"
class ProjectNotionPush(NotionPush):
    def __init__(self, apiKey, debug=False):
        super().__init__(apiKey, debug)
        self.page_dict = {}
        self.visited_url = {}
        self.project_db = "fb70b359848f498facfc4520b42225b4"
        self.query_page()
    def query_page(self):
        page = self.bot.blocks.children.list(self.project_db)
        for p in page["results"]:
            self.page_dict[p['child_database']['title']] = p["id"]
        #query all visited link
        for _, page_id in self.page_dict.items():
            self.visited_url = {**self.visited_url, **self.load_page(page_id)}
        print(f"visited url: {len(self.visited_url)}")
    def create_new_page(self, page_name):
        properties = {
        "Name": {"title": {}},  # This is a required property
        "URL": {"url": {}},
        "Description": {"rich_text": {}},
        "Star": {"number": {"format": "number_with_commas"}},
        "Fork": {"number": {"format": "number_with_commas"}},
       
        "Last Update": {"date": {}},
        "Language": {
            "type": "multi_select",
            "multi_select": {
                "options": [
                ]
                },
            },
        }
        title = [{"type": "text", "text": {"content": page_name}}]
        icon = {"type": "emoji", "emoji": "📒"}
        parent = {"type": "page_id", "page_id": self.project_db}
        return self.bot.databases.create(
        parent=parent, title=title, properties=properties, icon=icon
        )
    def push_data(self, data:NotionItem, dst:str):
        new_page_props = {
                "Name": notion_util(data.name, "title"),
                "URL": notion_util(data.url, "url"),
                "Description": notion_util(data.description, "rich_text"),
                "Star": notion_util(data.star, "number"),
                "Fork": notion_util(data.fork, "number"),
                "Language": {"type": "multi_select", "multi_select": [{"name": data.language}]} if data.language else notion_util('unknown', "multi_select"),
                "Last Update": notion_util(data.last_update, "date") if data.last_update!=0 else None,
            }
        if data.last_update == 0:
            del new_page_props['Last Update']
        self.bot.pages.create(
                parent={"database_id": dst}, properties=new_page_props
            )
    def load_page(self, pageid):
        rs = {}
        next_cursor = ""
        while True:
            if next_cursor == "":
                result = self.bot.databases.query(pageid, page_size=400)
            else:
                result = self.bot.databases.query(pageid, start_cursor=next_cursor)
            for r in result["results"]:
                title = r["properties"]["URL"]["url"]
                rs[title] = r['id']
            if not result["has_more"]:
                break
            next_cursor = result["next_cursor"]
        return rs
api = read_json_file(f"{PATH}/key.json")
db = SqliteDBReader("/Users/tianchenzhong/Dropbox/TCCode/ML/project_classifier/db.sqlite")

notion_pusher = ProjectNotionPush(api['notion_key'])

def get_all_data():
    sql = "select title, url, star, fork, language, description, available, last_updated,item_type from learning where available = 1"
    rs = db.get_data(sql)
    for row in rs:
        yield NotionItem(*row)
        
def create_page():
    for item in get_all_data():
        if item.item_type not in notion_pusher.page_dict:
            new_page = notion_pusher.create_new_page(item.item_type)
            notion_pusher.page_dict[item.item_type] =  new_page['id']
        if item.url in notion_pusher.visited_url:
            continue
        new_dst = notion_pusher.page_dict[item.item_type]
        notion_pusher.push_data(item, new_dst)
        logger.info(f"Pushed {item.name} to {new_dst}")

create_page()