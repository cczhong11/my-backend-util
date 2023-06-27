import json
from DataPusher.IFTTTPush import IFTTTPush
from DataReader.DropboxReader import DropboxReader
from DataWriter.OpenAIDataWriter import OpenAIDataWriter
from constant import PATH

api = {}
with open(f"{PATH}/key.json") as f:
    api = json.load(f)
dropbox = DropboxReader(
    api["dropbox_key"], api["dropbox_secret"], api["dropbox_refresh"]
)
rs = dropbox.get_data("/日记录音", ["m4a"])
whisper = OpenAIDataWriter(api["openai"])
ifttt = IFTTTPush(api["ifttt_dayone_webhook"])
for entry in rs:
    print(entry[1])
    dropbox.download(entry[1], f"/Users/tianchenzhong/Downloads/日记/{entry[0]}")

    whisper.write_data(
        f"/Users/tianchenzhong/Downloads/日记/{entry[0]}",
        "/Users/tianchenzhong/Downloads/日记/",
        "whisper",
    )
    data = ""
    filename = ".".join(entry[0].split(".")[0:-1]) + ".txt"
    with open(f"/Users/tianchenzhong/Downloads/日记/{filename}") as f:
        data = f.read()
    print(data)
    new_data = whisper.improve_data(data)
    with open(f"/Users/tianchenzhong/Downloads/日记/{filename}", "w") as f:
        f.write(new_data)
    ifttt.push_data({"value1": new_data}, "dayone_trigger")
