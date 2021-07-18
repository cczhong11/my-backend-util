from .DataPusherBase import DataPusherBase
from telegram import Bot 

class TelegramPush(DataPusherBase):
    def __init__(self, api, debug=False):
        self.bot = Bot(token=api)
        self.debug = debug
    
    def push_data(self, data, dst):
        if self.debug:
            print(f"send {dst}: {data}")
            return {}
        self.bot.send_message(dst, data)
        return {"result":"success"}
    
    
    def health_check(self):
        return True
