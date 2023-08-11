from DataFetcher.AllTrailDataFetcher import AllTrailDataFetcher
from DataPusher.NotionAllTrailPush import NotionAllTrailPush
from web_util import read_json_file

from constant import PATH

api = read_json_file(f"{PATH}/key.json")
notion = NotionAllTrailPush(api["notion_key"])
all_trails = AllTrailDataFetcher(cookie="cookie/alltrail.cookie")
data = all_trails.get_data("data/all_trail.json")
for trail in data:
    notion.push_data(trail)
