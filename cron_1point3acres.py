from DataPusher.TelegramPush import TelegramPush
from constant import PATH
from DataFetcher.BBS1pointDataFetcher import BBS1pointDataFetcher
import json
import os
api = {}
with open(f"{PATH}/key.json") as f:
    api = json.load(f)

def run():
    bot = TelegramPush(api['telegram_tuisongzhushou'], False)
    # run health check
    job = BBS1pointDataFetcher(f"{PATH}/cookie/1point3acres.cookie", 'job')
    if not job.health_check():
        if not os.path.exists(f"{PATH}/1pointError"):
            bot.push_data("HEALTH check wrong for 1point3acres","67424809")
            os.system(f"touch {PATH}/1pointError")
        raise Exception("Job check failed")
    application = BBS1pointDataFetcher(f"{PATH}/cookie/1point3acres.cookie", 'application')
    if not application.health_check():
        raise Exception("application check failed")
    
    # get data 
    
    jobs = job.get_data()
    applications = application.get_data()
    
    # send data
    
    
    for feed in jobs:
        if "实习" not in feed:
            if "在职跳槽" in feed:
                    
                bot.push_data(feed,"@usinterview")
            else: 
                bot.push_data(feed,"@usnewgradinterview")    
        else:   
            bot.push_data(feed,"@usinterninterview")
    for feed in applications:
        bot.push_data(feed,"@usgradapplication")
        
if __name__ == '__main__':
    run()