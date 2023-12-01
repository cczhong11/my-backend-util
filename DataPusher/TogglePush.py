from .DataPusherBase import DataPusherBase
from requests.auth import HTTPBasicAuth
from log_util import get_logger

logger = get_logger()

import typing as t
import requests
import time
import json
from datetime import datetime


def floatHourToTime(x):
    t = int(x * 24 * 3600)  # convert to number of seconds
    return f"{str(t//3600).zfill(2)}:{str((t%3600)//60).zfill(2)}:{str(t%60).zfill(2)}"


def floatHourToSecond(x, y):
    t = int((y - x) * 24 * 3600)  # convert to number of seconds
    return int(t) + 1


def transfer(item, shortcodes) -> t.Tuple[str, str, int, str]:
    date = item[0]
    start_time = item[1]
    end_time = item[2]
    shortcode = item[3].upper()
    start_time = datetime.strptime(start_time, "%H:%M:%S")
    end_time = datetime.strptime(end_time, "%H:%M:%S")
    duration = (end_time - start_time).seconds
    timezone = datetime.now(datetime.now().astimezone().tzinfo).isoformat()
    return (
        shortcodes[shortcode][0],
        shortcodes[shortcode][1],
        duration,
        f"{date}T{item[1]}{timezone[-6:]}",
    )


class TogglePush(DataPusherBase):
    def __init__(self, shortcodes, api, project_map, debug=False):
        self.shortcodes = shortcodes
        self.debug = debug
        self.api = api
        self.project_map = project_map

    def push_data(self, data):
        # TODO: skip the time entries already in
        for item in data:
            if len(item) == 5:
                if item[4] == "1":
                    continue
            if item[0] == "":
                continue
            project, description, duration, event_time = transfer(item, self.shortcodes)
            data = {
                "time_entry": {
                    "description": description,
                    "duration": duration,
                    "start": event_time,
                    "pid": self.project_map[project],
                    "created_with": "curl",
                }
            }
            if self.debug:
                logger.info(f"sending: {json.dumps(data)}")
                continue
            time.sleep(0.5)
            rs = requests.post(
                "https://api.track.toggl.com/api/v8/time_entries",
                auth=HTTPBasicAuth(self.api, "api_token"),
                data=json.dumps(data),
                headers={"Content-Type": "application/json"},
            ).content

    def health_check(self):
        return True
