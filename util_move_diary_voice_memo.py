from dataclasses import dataclass
import os
import shutil
import sqlite_util
from DataWriter.OpenAIDataWriter import OpenAIDataWriter
from DataPusher.IFTTTPush import IFTTTPush
import json
import time
from log_util import get_logger
from constant import PATH

logger = get_logger("util_move_diary_voice_memo")
api = {}
with open(f"{PATH}/key.json") as f:
    api = json.load(f)


whisper = OpenAIDataWriter(api["openai"])
ifttt = IFTTTPush(api["ifttt_dayone_webhook"])
"""
CREATE TABLE ZCLOUDRECORDING ( Z_PK INTEGER PRIMARY KEY, Z_ENT INTEGER, Z_OPT INTEGER, ZFLAGS INTEGER, ZSHAREDFLAGS INTEGER, ZFOLDER INTEGER, ZDATE TIMESTAMP, ZDURATION FLOAT, ZEVICTIONDATE TIMESTAMP, ZLOCALDURATION FLOAT, ZCUSTOMLABEL VARCHAR, ZCUSTOMLABELFORSORTING VARCHAR, ZENCRYPTEDTITLE VARCHAR, ZPATH VARCHAR, ZUNIQUEID VARCHAR, ZAUDIODIGEST BLOB, ZAUDIOFUTURE BLOB , ZAUDIOFUTUREUUIDS BLOB);

select ZENCRYPTEDTITLE, ZPATH from ZCLOUDRECORDING where ZFOLDER=1 ; // for 日记


"""


@dataclass
class VoiceMemo:
    title: str
    path: str
    folder: int


download_path = "/Users/tianchenzhong/Downloads/日记/"
# Define the source and destination directories
source_directory = "/Users/tianchenzhong/Library/Group Containers/group.com.apple.VoiceMemos.shared/Recordings"
destination_directory = "/Users/tianchenzhong/Dropbox/Apps/tc-memo/日记录音"
other_destination_directory = "/Users/tianchenzhong/Downloads/mp3/语言转文字"
read_book_destination_directory = (
    "/Users/tianchenzhong/Documents/lora_train/ztc_read_book"
)
db = os.path.join(source_directory, "CloudRecordings.db")
result = sqlite_util.select_database(
    db,
    "SELECT ZENCRYPTEDTITLE, ZPATH, ZFOLDER FROM ZCLOUDRECORDING ORDER BY ZDATE DESC LIMIT 10",
)
voice_memos = []
new_paths = []
for r in result:
    voice_memo = VoiceMemo(r[0], r[1], r[2])
    voice_memos.append(voice_memo)
    real_path = os.path.join(source_directory, voice_memo.path)
    if voice_memo.folder == 1:
        new_path = os.path.join(download_path, voice_memo.title + ".m4a")
    if voice_memo.folder == 6:
        new_path = os.path.join(
            read_book_destination_directory, voice_memo.title + ".m4a"
        )
    else:
        new_path = os.path.join(other_destination_directory, voice_memo.title + ".m4a")
    if os.path.exists(new_path):
        continue
    shutil.copy(real_path, new_path)
    logger.info(
        f"Successfully copied the latest file {os.path.basename(new_path)} to {new_path} uwu"
    )
    new_paths.append(new_path)
for path in new_paths:
    if "ztc_read_book" in path:
        continue
    whisper.write_data(
        path,
        os.path.dirname(path),
        "whisper",
    )
    data = ""
    newfilename = ".".join(path.split(".")[0:-1]) + ".txt"
    with open(newfilename) as f:
        data = f.read()
    new_data = whisper.improve_data(data)
    time.sleep(5)
    newfilename2 = ".".join(path.split(".")[0:-1]) + "_edit.txt"
    with open(newfilename2, "w") as f:
        f.write(new_data)
    base_name = os.path.basename(path).split(".")[0]
    if "日记" in path:
        newfilename3 = ".".join(path.split(".")[0:-1]) + "_final.txt"
        suggestion = whisper.suggest_data(new_data)
        processed_data = data + "\n" + suggestion
        with open(newfilename3, "w") as f:
            f.write(processed_data)
        ifttt.push_data({"value1": base_name + "\n" + processed_data}, "dayone_trigger")
    logger.info(f"Successfully processed the file {os.path.basename(path)} uwu")
