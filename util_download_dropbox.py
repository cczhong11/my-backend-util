import json
from DataReader.DropboxReader import DropboxReader
from DataWriter.OpenAIDataWriter import OpenAIDataWriter
from constant import PATH

api = {}
with open(f"{PATH}/key.json") as f:
    api = json.load(f)
dropbox = DropboxReader(api["dropbox_access"])
rs = dropbox.get_data("/日记录音", ["m4a"])
for entry in rs:
    print(entry[1])
    dropbox.download(entry[1], f"/Users/tianchenzhong/Downloads/{entry[0]}")
whisper = OpenAIDataWriter(api["openai"])
whisper.write_data(
    "/Users/tianchenzhong/Downloads/66日记.m4a",
    "/Users/tianchenzhong/Downloads",
    "whisper",
)
