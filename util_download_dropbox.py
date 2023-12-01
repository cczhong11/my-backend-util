import json
from DataPusher.IFTTTPush import IFTTTPush
from DataReader.DropboxReader import DropboxReader
from DataWriter.OpenAIDataWriter import OpenAIDataWriter
from constant import PATH
import os

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
    if not os.path.exists(f"/Users/tianchenzhong/Downloads/日记/{entry[0]}"):
        dropbox.download(entry[1], f"/Users/tianchenzhong/Downloads/日记/{entry[0]}")
    # handle exist inside
    whisper.write_data(
        f"/Users/tianchenzhong/Downloads/日记/{entry[0]}",
        "/Users/tianchenzhong/Downloads/日记/",
        "whisper",
    )
    data = ""
    base = ".".join(entry[0].split(".")[0:-1])
    filename = base + ".txt"
    with open(f"/Users/tianchenzhong/Downloads/日记/{filename}") as f:
        data = f.read()
    edit_filename = base + "_edit.txt"
    if not os.path.exists(f"/Users/tianchenzhong/Downloads/日记/{edit_filename}"):
        new_data = whisper.improve_data(data)
        with open(f"/Users/tianchenzhong/Downloads/日记/{edit_filename}", "w") as f:
            f.write(new_data)
    with open(f"/Users/tianchenzhong/Downloads/日记/{edit_filename}") as f:
        new_data = f.read()
    final_filename = base + "_final.txt"
    if not os.path.exists(f"/Users/tianchenzhong/Downloads/日记/{final_filename}"):
        suggestion = whisper.suggest_data(new_data)
        new_data = base + "\n" + new_data + "\n" + suggestion
        with open(f"/Users/tianchenzhong/Downloads/日记/{final_filename}", "w") as f:
            f.write(new_data)
    with open(f"/Users/tianchenzhong/Downloads/日记/{final_filename}") as f:
        new_data = f.read()
    ifttt.push_data({"value1": new_data}, "dayone_trigger")
