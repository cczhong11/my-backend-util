from .DataPusherBase import DataPusherBase
import requests
from log_util import get_logger

logger = get_logger()


class IFTTTPush(DataPusherBase):
    def __init__(self, dst_url, debug=False):
        self.debug = debug
        self.dst_url = dst_url

    def push_data(self, data, dst):
        if self.debug:
            print(f"send {dst}: {data}")
            return {}
        requests.post(
            f"https://maker.ifttt.com/trigger/{dst}/with/key/{self.dst_url}",
            json=data,
        )

    def health_check(self):
        return True
