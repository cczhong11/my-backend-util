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
daily_think = dropbox.get_data("/每日心得", ["m4a"])
whisper = OpenAIDataWriter(api["openai"])
ifttt = IFTTTPush(api["ifttt_dayone_webhook"])
download_path = "/Users/tianchenzhong/Downloads/日记/"

import chardet


def read_file_with_correct_encoding(file_path):
    with open(file_path, "r", encoding="utf-8", errors="ignore") as f:
        data = f.read()
    return data


def download_file(entry):
    file_path = os.path.join(download_path, entry[0])
    if not os.path.exists(file_path):
        dropbox.download(entry[1], file_path)
    base_name = ".".join(entry[0].split(".")[0:-1])
    txt_path = os.path.join(download_path, f"{base_name}.txt")
    if os.path.exists(txt_path):
        return
    whisper.write_data(
        file_path,
        download_path,
        "whisper",
    )


def process_file(entry, process_type, suffix):
    base_name = ".".join(entry[0].split(".")[0:-1])
    file_path = os.path.join(download_path, f"{base_name}.txt")

    if process_type == "suggest":
        file_path = os.path.join(download_path, f"{base_name}_edit.txt")
    new_file_path = os.path.join(download_path, f"{base_name}_{suffix}.txt")

    if not os.path.exists(new_file_path):
        data = read_file_with_correct_encoding(file_path)

        if process_type == "improve":
            processed_data = whisper.improve_data(data)
        elif process_type == "suggest":
            suggestion = whisper.suggest_data(data)
            processed_data = data + "\n" + suggestion

        with open(new_file_path, "w") as f:
            f.write(processed_data)


def push_data(entry, suffix):
    base_name = ".".join(entry[0].split(".")[0:-1])
    final_file_path = os.path.join(download_path, f"{base_name}_{suffix}.txt")

    with open(final_file_path) as f:
        data = f.read()

    ifttt.push_data({"value1": base_name + "\n" + data}, "dayone_trigger")


def process_entries(rs, skip_suggest=False):
    for entry in rs:
        print(entry[1])
        download_file(entry)
        process_file(entry, "improve", "edit")
        if not skip_suggest:
            process_file(entry, "suggest", "final")
            push_data(entry, "final")
        else:
            push_data(entry, "edit")


# Example usage
process_entries(rs)
process_entries(daily_think, skip_suggest=True)
