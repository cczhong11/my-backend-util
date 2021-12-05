from DataFetcher.WeiboDataFetcher import WeiboDataFetcher
from DataWriter.MarkdownImgDownloader import MarkdownImgDownloader
from constant import PATH
import os
from pathlib import Path

BQB_PATH = os.path.join(str(Path.home()), "Documents", "bqb")


def run():
    with open(f"{PATH}/cookie/weibo.cookie") as f:
        cookie = f.read()
    wb = WeiboDataFetcher(cookie)
    path = wb.get_data()

    md = MarkdownImgDownloader(path, BQB_PATH)
    md.write_data()


run()
