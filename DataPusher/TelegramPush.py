from .DataPusherBase import DataPusherBase
from telegram import Bot
from log_util import get_logger

logger = get_logger()

import asyncio


class TelegramPush(DataPusherBase):
    def __init__(self, api, debug=False):
        self.bot = Bot(token=api)
        self.debug = debug

    def push_data(self, data, dst):
        if self.debug:
            print(f"send {dst}: {data}")
            return {}
        asyncio.run(self.bot.send_message(dst, data))

        logger.info(f"send {dst}: {data}")
        return {"result": "success"}

    def push_picture(self, data, dst):
        if self.debug:
            print(f"send picture {data} to {dst}")
            return {}
        if ".gif" in data:
            asyncio.run(self.bot.send_document(dst, data))
        else:
            asyncio.run(self.bot.send_photo(dst, data))

    def health_check(self):
        return True
