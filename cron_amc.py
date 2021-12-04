from DataFetcher.AMCMovieDataFetcher import AMCMovieDataFetcher
from DataFetcher.DoubanFetcher import DoubanFetcher
from DataPusher.NotionPush import NotionPush, notion_util

from web_util import read_json_file
from constant import PATH
from log_util import logger
import sys


def run():
    # health_check
    api = read_json_file(f"{PATH}/key.json")
    amc = AMCMovieDataFetcher(api["amc_key"])
    douban = DoubanFetcher(f"{PATH}/cookie/douban.cookie", "movie")
    notion_push = NotionPush(api["notion_key"])
    if not amc.health_check():
        logger.exception("amc health check failed")
        sys.exit(1)
    if not douban.health_check():
        logger.exception("douban health check failed")
        sys.exit(1)
    # get data
    data = amc.get_data("")
    current_data = notion_push.get_current_data("AMC")
    current_movie = set()
    for movie in data["data"]:
        current_movie.add(movie["name"])
        if movie["name"] in current_data and current_data[movie["name"]][1] != -1:
            continue
        douban_info = douban.get_data(movie["imdb"])
        movie["douban"] = douban_info.get("rating", -1)
        movie["douban_url"] = douban_info.get("href", None)
        movie["chinese_name"] = douban_info.get("title", "")
        if movie["name"] not in current_data:
            notion_push.push_data(movie, "AMC")
        else:
            notion_push.update_page(
                current_data[movie["name"]][0],
                properties={"douban": notion_util(movie["douban"], "number")},
            )
    for m in current_data:
        if m not in current_movie:
            notion_push.update_page(current_data[m][0], archived=True)


if __name__ == "__main__":
    run()
