from .DataPusherBase import DataPusherBase
from notion_client import Client
from log_util import logger
AMC_DB = "d0ed80f8b0ce4d8bb6aa4c6e6bfeaa6c"
class NotionPush(DataPusherBase):
    def __init__(self, api,debug=False):
        self.bot = Client(auth=api)
        self.debug = debug
    
    def push_data(self, data, dst):
        if self.debug:
            print(f"send {dst}: {data}")
            return {}
        if dst == "AMC":
            new_page_props = {
                'Title': {'title': [{'text': {'content': data['name']}}]},
                'Genre': {'type': 'multi_select', 'multi_select': [{'name': data['genre']}]},
                'imdb':  { "type":'url','url':f'https://www.imdb.com/title/{data["imdb"]}' },
                'douban_url':{ "type":'url','url':data['douban_url']},
                'chinese_name' : { "rich_text": [ { "text": { "content":data['chinese_name'] } } ] },
                'douban': {'number': data['douban']},
                'Link': {'type': 'url', 'url': data['url']},  
            }
            self.bot.pages.create(
            parent={'database_id': AMC_DB },
            properties=new_page_props)
        logger.info(f"send {dst}: {data}")
        return {"result":"success"}
    
    def get_current_data(self, topic):
        rs = {}
        if topic == 'AMC':
            result = self.bot.databases.query(AMC_DB)
            for r in result['results']:
                try:
                    rs[r['properties']['Title']['title'][0]['text']['content']]=r['id']   
                except:
                    continue
        return rs
    
    def health_check(self):
        return True
