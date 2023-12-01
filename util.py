import os
import json

from constant import PATH


def read_json_file(file_path):
    with open(file_path, "r") as file:
        data = json.load(file)
    return data


def get_rss_path():
    config = read_json_file(f"{PATH}/config.json")

    os_name = os.uname().nodename
    config_path = "rss_path"
    if "MacBook" in os_name:
        config_path = "mac_rss_path"
    if "mbp" in os_name:
        config_path = "darwin_rss_path"
    return config[config_path]


def get_tts_path():
    config = read_json_file(f"{PATH}/config.json")

    os_name = os.uname().nodename
    config_path = "tts_path"
    if "MacBook" in os_name:
        config_path = "mac_tts_path"
    return config[config_path]
