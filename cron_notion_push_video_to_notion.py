from DataPusher.NotionVideoPush import NotionVideoPush
from DataReader.SqliteDBReader import SqliteDBReader
from constant import PATH
from util import read_json_file


reader = SqliteDBReader("/Users/tianchenzhong/Dropbox/db/my_life_summary.db")
result = reader.get_data(
    "SELECT file_name, description, focal_length, duration, size FROM videos where file_name like '%2023_11_18%'"
)
datas = [
    {
        "file_name": row[0],
        "description": row[1] or "",
        "focal_length": row[2] or "",
        "duration": row[3],
        "size": row[4],
    }
    for row in result
    if "抱歉，我无法完成此任务" not in row[1]
]
api = read_json_file(f"{PATH}/key.json")
push = NotionVideoPush(api["notion_key"])
for data in datas:
    push.push_data(data)
