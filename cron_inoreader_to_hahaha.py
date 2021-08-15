from DataPusher.TelegramPush import TelegramPush
from constant import PATH
from DataFetcher.InoReaderDataFetcher import InoReaderDataFetcher
import json
import sys
import os
from log_util import logger
api = {}
with open(f"{PATH}/key.json") as f:
    api = json.load(f)

def run():
    bot = TelegramPush(api['telegram_tuisongzhushou'], False)
    # run health check
    hahaha = InoReaderDataFetcher(f"{PATH}/cookie/inoreader.cookie", 'star')
    if not hahaha.health_check():
        logger.exception("hahaha check failed")
        sys.exit(1)
    
    # get data 
    pics = hahaha.starrd_hahaha_process()
    
    # send data    
    for pic in pics:
        logger.info(pic)
        bot.push_picture(pic,"@funnypicdaily")
        
if __name__ == '__main__':
    try:
        run()
    except Exception as e:
        logger.exception(str(e))