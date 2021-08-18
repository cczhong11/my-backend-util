from DataReader.FileDataReader import FileDataReader
from DataWriter.AWSS3DataWriter import AWSS3DataWriter
from log_util import logger
import os
from constant import PATH
import pickle
from datetime import datetime
from web_util import read_json_file
import pytz
need_list = ["精进2","蛤蟆","学会提问"]
SUBFIX = ".mp3"
MOBI = "/Users/tczhong/Documents/mobi2mp3"


def check_filename(filename, need_list):
    for item in need_list:
        if item in filename:
            return True
    return False

def run():
    filereader = FileDataReader(MOBI)
    s3 = AWSS3DataWriter("rss-ztc")
    if not filereader.health_check():
        logger.exception("filereader health check failed")
    data = filereader.get_list("")
    for item in data:
        filename = item['name']
        if check_filename(filename, need_list) and SUBFIX in filename:
            s3.write_data("book", os.path.join(MOBI, filename))
            logger.info(f"upload {filename}")
            
if __name__ == '__main__':
    run()