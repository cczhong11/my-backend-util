from .DataPusherBase import DataPusherBase
from telegram import Bot 

class TelegramPush(DataPusherBase):
    def __init__(self, api):
        self.bot = Bot(token=api)
    
    def push_data(self, data, dst):
        self.bot.send_message(dst, data)
        return {"result":"success"}
    
    
    def health_check(self):
        return True
