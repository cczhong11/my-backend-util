from DataWriter.AWSS3DataWriter import AWSS3DataWriter
from constant import PATH
from DataReader.GoogleSheetReader import GoogleSheetReader
from DataFetcher.TTSFetcher import TTSFetcher
import json
import sys
import os
from log_util import get_logger
from util import get_tts_path

logger = get_logger()

from DataExtractor.WechatExtractor import WechatExtractor

tts_path = get_tts_path()
api = {}
with open(f"{PATH}/key.json") as f:
    api = json.load(f)


def run():
    Gsheet = GoogleSheetReader(f"{PATH}/cookie/service_account.json", api["tts_sheet"])
    items = Gsheet.get_data("Sheet1")
    tts = TTSFetcher(f"{PATH}/cookie/tts-google.json", tts_path)
    s3 = AWSS3DataWriter("rss-ztc")

    data = []
    for line in items:
        if "https:" in line[0]:
            if "mp.weixin.qq.com" in line[0]:
                tts.get_wechat_data(line[0], f"{PATH}/cookie/wechat.cookie")
            else:
                tts.get_data(line[0])
            s3.write_data(
                "articles",
                os.path.join(tts_path, f"{tts.current_title()}.mp3"),
            )
        else:
            data.append(line)

    Gsheet.sheet.sheet1.clear()
    Gsheet.sheet.sheet1.update("A1", data)


if __name__ == "__main__":
    try:
        run()
    except Exception as e:
        logger.exception(str(e))
